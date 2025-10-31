import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ScrollView,
  Platform,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import apiClient from '../api/client';
import { formatTime, formatSportName } from '../utils/formatters';
import {
  getTennisGameScore,
  isGameWon,
  isSetWon,
  isTiebreaker,
  isTiebreakWon,
  isMatchWon,
  formatSetScores,
} from '../utils/tennisScoring';

export default function ActiveSessionScreen({ navigation, route }) {
  const { session } = route.params;
  const [elapsedTime, setElapsedTime] = useState(0);
  const [isPaused, setIsPaused] = useState(false);
  const [authToken, setAuthToken] = useState('');

  // Parse metadata
  const metadata = session.metadata ? JSON.parse(session.metadata) : {};
  const isTennisRegular = (session.sport === 'tennis' || session.sport === 'padel') && session.scoring_system === 'regular';
  const bestOfGames = metadata.best_of_games || 1;

  // Score tracking state (for matches only)
  const [scoreMe, setScoreMe] = useState(0);
  const [scoreOpponent, setScoreOpponent] = useState(0);
  const [gameNumber, setGameNumber] = useState(1);
  const [points, setPoints] = useState([]);

  // Tennis-specific state
  const [tennisGamePointsMe, setTennisGamePointsMe] = useState(0);
  const [tennisGamePointsOpponent, setTennisGamePointsOpponent] = useState(0);
  const [tennisGamesMe, setTennisGamesMe] = useState(0);
  const [tennisGamesOpponent, setTennisGamesOpponent] = useState(0);
  const [tennisSetScores, setTennisSetScores] = useState([]); // Array of {me: X, opponent: Y}
  const [tennisCurrentSet, setTennisCurrentSet] = useState(1);
  const [tennisInTiebreak, setTennisInTiebreak] = useState(false);
  const [tennisTiebreakPointsMe, setTennisTiebreakPointsMe] = useState(0);
  const [tennisTiebreakPointsOpponent, setTennisTiebreakPointsOpponent] = useState(0);

  useEffect(() => {
    // Calculate initial elapsed time
    const startTime = new Date(session.start_time);
    const now = new Date();
    const initialElapsed = Math.floor((now - startTime) / 1000);
    setElapsedTime(initialElapsed);

    // Start timer
    const interval = setInterval(() => {
      if (!isPaused) {
        setElapsedTime((prev) => prev + 1);
      }
    }, 1000);

    return () => clearInterval(interval);
  }, [isPaused, session.start_time]);

  // Load existing points on mount (for matches)
  useEffect(() => {
    if (session.session_type === 'match') {
      loadPoints();
    }
  }, []);

  // Load auth token for watch app
  useEffect(() => {
    const loadToken = async () => {
      const token = await AsyncStorage.getItem('@squash_analytics_token');
      setAuthToken(token || 'No token found');
    };
    loadToken();
  }, []);

  // Auto-refresh points every 5 seconds (for watch sync)
  useEffect(() => {
    if (session.session_type === 'match') {
      const refreshInterval = setInterval(() => {
        loadPoints();
      }, 5000); // Poll every 5 seconds

      return () => clearInterval(refreshInterval);
    }
  }, [session.session_type]);

  const loadPoints = async () => {
    try {
      const existingPoints = await apiClient.getPoints(session.session_id);
      setPoints(existingPoints);

      // Calculate current score from points
      if (existingPoints.length > 0) {
        const lastPoint = existingPoints[existingPoints.length - 1];
        setScoreMe(lastPoint.score_me_after);
        setScoreOpponent(lastPoint.score_opponent_after);
        setGameNumber(lastPoint.game_number);
      }
    } catch (error) {
      // Error loading points - silently fail for now
    }
  };

  const recordPoint = async (winner, isLet = false) => {
    const newScoreMe = winner === 'me' && !isLet ? scoreMe + 1 : scoreMe;
    const newScoreOpponent = winner === 'opponent' && !isLet ? scoreOpponent + 1 : scoreOpponent;

    try {
      const pointData = {
        winner: winner,
        score_me_before: scoreMe,
        score_opponent_before: scoreOpponent,
        score_me_after: newScoreMe,
        score_opponent_after: newScoreOpponent,
        game_number: gameNumber,
        is_let: isLet ? "true" : "false",
      };

      const newPoint = await apiClient.recordPoint(session.session_id, pointData);
      setPoints([...points, newPoint]);
      setScoreMe(newScoreMe);
      setScoreOpponent(newScoreOpponent);
    } catch (error) {
      let errorMessage = 'Failed to record point.';

      if (error && error.message) {
        // If message is an object, convert it to string
        if (typeof error.message === 'object') {
          try {
            errorMessage = JSON.stringify(error.message);
          } catch (e) {
            errorMessage = 'Error: Could not parse error details';
          }
        } else {
          errorMessage = error.message;
        }
      } else if (typeof error === 'string') {
        errorMessage = error;
      } else {
        errorMessage = 'Unknown error occurred';
      }

      if (Platform.OS === 'web') {
        alert('Error recording point: ' + errorMessage);
      } else {
        Alert.alert('Error Recording Point', errorMessage);
      }
    }
  };

  const recordTennisPoint = (winner) => {
    if (tennisInTiebreak) {
      // Handle tiebreaker point
      const newPointsMe = winner === 'me' ? tennisTiebreakPointsMe + 1 : tennisTiebreakPointsMe;
      const newPointsOpponent = winner === 'opponent' ? tennisTiebreakPointsOpponent + 1 : tennisTiebreakPointsOpponent;

      setTennisTiebreakPointsMe(newPointsMe);
      setTennisTiebreakPointsOpponent(newPointsOpponent);

      // Check if tiebreaker is won
      const tiebreakWinner = isTiebreakWon(newPointsMe, newPointsOpponent);
      if (tiebreakWinner) {
        // Tiebreak set score is 7-6
        const newGamesMe = tiebreakWinner === 'me' ? 7 : 6;
        const newGamesOpponent = tiebreakWinner === 'opponent' ? 7 : 6;

        // Add completed set
        const newSetScores = [...tennisSetScores, { me: newGamesMe, opponent: newGamesOpponent }];
        setTennisSetScores(newSetScores);

        // Check if match is won
        const setsMe = newSetScores.filter(s => s.me > s.opponent).length;
        const setsOpponent = newSetScores.filter(s => s.opponent > s.me).length;
        const matchWinner = isMatchWon(setsMe, setsOpponent, bestOfGames);

        if (matchWinner) {
          Alert.alert('Match Won!', `${matchWinner === 'me' ? 'You' : 'Opponent'} won the match!`);
        } else {
          // Start next set
          setTennisCurrentSet(tennisCurrentSet + 1);
          setTennisGamesMe(0);
          setTennisGamesOpponent(0);
          setTennisInTiebreak(false);
          setTennisTiebreakPointsMe(0);
          setTennisTiebreakPointsOpponent(0);
          setTennisGamePointsMe(0);
          setTennisGamePointsOpponent(0);
        }
      }
    } else {
      // Handle regular game point
      const newPointsMe = winner === 'me' ? tennisGamePointsMe + 1 : tennisGamePointsMe;
      const newPointsOpponent = winner === 'opponent' ? tennisGamePointsOpponent + 1 : tennisGamePointsOpponent;

      setTennisGamePointsMe(newPointsMe);
      setTennisGamePointsOpponent(newPointsOpponent);

      // Check if game is won
      const gameWinner = isGameWon(newPointsMe, newPointsOpponent);
      if (gameWinner) {
        const newGamesMe = gameWinner === 'me' ? tennisGamesMe + 1 : tennisGamesMe;
        const newGamesOpponent = gameWinner === 'opponent' ? tennisGamesOpponent + 1 : tennisGamesOpponent;

        setTennisGamesMe(newGamesMe);
        setTennisGamesOpponent(newGamesOpponent);
        setTennisGamePointsMe(0);
        setTennisGamePointsOpponent(0);

        // Check for tiebreaker
        if (isTiebreaker(newGamesMe, newGamesOpponent)) {
          setTennisInTiebreak(true);
          setTennisTiebreakPointsMe(0);
          setTennisTiebreakPointsOpponent(0);
        } else {
          // Check if set is won
          const setWinner = isSetWon(newGamesMe, newGamesOpponent);
          if (setWinner) {
            // Add completed set
            const newSetScores = [...tennisSetScores, { me: newGamesMe, opponent: newGamesOpponent }];
            setTennisSetScores(newSetScores);

            // Check if match is won
            const setsMe = newSetScores.filter(s => s.me > s.opponent).length;
            const setsOpponent = newSetScores.filter(s => s.opponent > s.me).length;
            const matchWinner = isMatchWon(setsMe, setsOpponent, bestOfGames);

            if (matchWinner) {
              Alert.alert('Match Won!', `${matchWinner === 'me' ? 'You' : 'Opponent'} won the match!`);
            } else {
              // Start next set
              setTennisCurrentSet(tennisCurrentSet + 1);
              setTennisGamesMe(0);
              setTennisGamesOpponent(0);
            }
          }
        }
      }
    }
  };

  const handleUndoPoint = async () => {
    if (points.length === 0) {
      if (Platform.OS === 'web') {
        alert('No points to undo');
      } else {
        Alert.alert('Info', 'No points to undo');
      }
      return;
    }

    try {
      await apiClient.undoLastPoint(session.session_id);
      const updatedPoints = points.slice(0, -1);
      setPoints(updatedPoints);

      // Restore previous score
      if (updatedPoints.length > 0) {
        const lastPoint = updatedPoints[updatedPoints.length - 1];
        setScoreMe(lastPoint.score_me_after);
        setScoreOpponent(lastPoint.score_opponent_after);
        setGameNumber(lastPoint.game_number);
      } else {
        setScoreMe(0);
        setScoreOpponent(0);
        setGameNumber(1);
      }
    } catch (error) {
      const errorMessage = error.message || error.toString() || 'Failed to undo point';
      if (Platform.OS === 'web') {
        alert('Error undoing point: ' + errorMessage);
      } else {
        Alert.alert('Error', errorMessage);
      }
    }
  };

  const handleNextGame = () => {
    if (Platform.OS === 'web') {
      const confirmed = window.confirm(
        `Current game score: ${scoreMe}-${scoreOpponent}\n\nStart next game?`
      );
      if (confirmed) {
        setGameNumber(gameNumber + 1);
        setScoreMe(0);
        setScoreOpponent(0);
      }
    } else {
      Alert.alert(
        'Next Game',
        `Current game score: ${scoreMe}-${scoreOpponent}\n\nStart next game?`,
        [
          {
            text: 'Cancel',
            style: 'cancel',
          },
          {
            text: 'Next Game',
            onPress: () => {
              setGameNumber(gameNumber + 1);
              setScoreMe(0);
              setScoreOpponent(0);
            },
          },
        ]
      );
    }
  };

  const handlePauseResume = () => {
    setIsPaused(!isPaused);
  };

  const calculateFinalScores = () => {
    if (session.session_type !== 'match' || points.length === 0) {
      return {
        gameScores: [],
        gamesWonMe: 0,
        gamesWonOpponent: 0,
        totalGames: 0,
      };
    }

    // Group points by game number
    const gameMap = {};
    points.forEach(point => {
      if (!gameMap[point.game_number]) {
        gameMap[point.game_number] = [];
      }
      gameMap[point.game_number].push(point);
    });

    // Get final score for each game
    const gameScores = [];
    let gamesWonMe = 0;
    let gamesWonOpponent = 0;

    Object.keys(gameMap).sort((a, b) => parseInt(a) - parseInt(b)).forEach(gameNum => {
      const gamePoints = gameMap[gameNum];
      const lastPoint = gamePoints[gamePoints.length - 1];
      const scoreMe = lastPoint.score_me_after;
      const scoreOpponent = lastPoint.score_opponent_after;

      gameScores.push(`${scoreMe}-${scoreOpponent}`);

      if (scoreMe > scoreOpponent) {
        gamesWonMe++;
      } else if (scoreOpponent > scoreMe) {
        gamesWonOpponent++;
      }
    });

    return {
      gameScores,
      gamesWonMe,
      gamesWonOpponent,
      totalGames: Object.keys(gameMap).length,
    };
  };

  const handleEndSession = async () => {
    if (Platform.OS === 'web') {
      const confirmed = window.confirm('Are you sure you want to end this session?');
      if (confirmed) {
        try {
          const { gameScores, gamesWonMe, gamesWonOpponent, totalGames } = calculateFinalScores();

          const updateData = {
            end_time: new Date().toISOString(),
          };

          if (session.session_type === 'match' && points.length > 0) {
            updateData.final_score_me = gamesWonMe;
            updateData.final_score_opponent = gamesWonOpponent;
            updateData.total_games = totalGames;
            updateData.total_points = points.length;
            updateData.metadata = JSON.stringify({
              game_scores: gameScores.join(' '),
            });
          }

          await apiClient.updateSession(session.session_id, updateData);

          const viewDetails = window.confirm(
            'Session ended successfully!\n\nClick OK to view details, or Cancel to view all sessions.'
          );

          // Navigate to parent tab navigator first
          const parentNav = navigation.getParent();
          if (viewDetails) {
            parentNav.navigate('SessionList', {
              screen: 'SessionDetails',
              params: { sessionId: session.session_id },
            });
          } else {
            parentNav.navigate('SessionList', {
              screen: 'SessionListMain',
            });
          }
        } catch (error) {
          alert('Error: ' + error.message);
        }
      }
    } else {
      Alert.alert(
        'End Session',
        'Are you sure you want to end this session?',
        [
          {
            text: 'Cancel',
            style: 'cancel',
          },
          {
            text: 'End Session',
            style: 'destructive',
            onPress: async () => {
              try {
                const { gameScores, gamesWonMe, gamesWonOpponent, totalGames } = calculateFinalScores();

                const updateData = {
                  end_time: new Date().toISOString(),
                };

                if (session.session_type === 'match' && points.length > 0) {
                  updateData.final_score_me = gamesWonMe;
                  updateData.final_score_opponent = gamesWonOpponent;
                  updateData.total_games = totalGames;
                  updateData.total_points = points.length;
                  updateData.metadata = JSON.stringify({
                    game_scores: gameScores.join(' '),
                  });
                }

                await apiClient.updateSession(session.session_id, updateData);

                Alert.alert(
                  'Session Ended',
                  'Your session has been saved successfully!',
                  [
                    {
                      text: 'View Details',
                      onPress: () => {
                        const parentNav = navigation.getParent();
                        parentNav.navigate('SessionList', {
                          screen: 'SessionDetails',
                          params: { sessionId: session.session_id },
                        });
                      },
                    },
                    {
                      text: 'View Sessions',
                      onPress: () => {
                        const parentNav = navigation.getParent();
                        parentNav.navigate('SessionList', {
                          screen: 'SessionListMain',
                        });
                      },
                    },
                  ]
                );
              } catch (error) {
                Alert.alert('Error', error.message);
              }
            },
          },
        ]
      );
    }
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.content}>
        {/* Session Info */}
        <View style={styles.infoCard}>
          <Text style={styles.sportLabel}>{formatSportName(session.sport)}</Text>
          <Text style={styles.sessionType}>
            {session.session_type === 'match' ? 'Match' : 'Training Session'}
          </Text>
          <Text style={styles.sessionId} selectable={true}>
            ID: {session.session_id}
          </Text>
          <Text style={styles.authToken} selectable={true}>
            Token: {authToken}
          </Text>
        </View>

        {/* Timer */}
        <View style={styles.timerCard}>
          <Text style={styles.timerLabel}>Elapsed Time</Text>
          <Text style={styles.timerDisplay}>{formatTime(elapsedTime)}</Text>
          <View style={[styles.statusBadge, isPaused && styles.pausedBadge]}>
            <Text style={styles.statusText}>
              {isPaused ? 'PAUSED' : 'ACTIVE'}
            </Text>
          </View>
        </View>

        {/* Refresh Button */}
        <TouchableOpacity
          style={styles.refreshButton}
          onPress={loadPoints}
        >
          <Text style={styles.refreshButtonText}>🔄 Refresh Points from Watch</Text>
        </TouchableOpacity>

        {/* Stats */}
        <View style={styles.statsCard}>
          <Text style={styles.statsTitle}>Session Stats</Text>
          <View style={styles.statsGrid}>
            <View style={styles.statItem}>
              <Text style={styles.statValue}>--</Text>
              <Text style={styles.statLabel}>Heart Rate</Text>
            </View>
            <View style={styles.statItem}>
              <Text style={styles.statValue}>--</Text>
              <Text style={styles.statLabel}>Calories</Text>
            </View>
            <View style={styles.statItem}>
              <Text style={styles.statValue}>--</Text>
              <Text style={styles.statLabel}>Distance</Text>
            </View>
            <View style={styles.statItem}>
              <Text style={styles.statValue}>--</Text>
              <Text style={styles.statLabel}>Points</Text>
            </View>
          </View>
          <Text style={styles.statsNote}>
            Stats will be available with smartwatch integration
          </Text>
        </View>

        {/* Score Tracking (Matches Only) */}
        {session.session_type === 'match' && !isTennisRegular && (
          <View style={styles.scoreCard}>
            <Text style={styles.scoreTitle}>Score - Game {gameNumber}</Text>

            {/* Current Score Display */}
            <View style={styles.scoreDisplay}>
              <View style={styles.scorePlayerSection}>
                <Text style={styles.scorePlayerLabel}>Me</Text>
                <Text style={styles.scorePlayerValue}>{scoreMe}</Text>
              </View>
              <Text style={styles.scoreDivider}>-</Text>
              <View style={styles.scorePlayerSection}>
                <Text style={styles.scorePlayerLabel}>Opponent</Text>
                <Text style={styles.scorePlayerValue}>{scoreOpponent}</Text>
              </View>
            </View>

            {/* Point Recording Buttons */}
            <Text style={styles.pointButtonsLabel}>Record Point:</Text>
            <View style={styles.pointButtonsRow}>
              <TouchableOpacity
                style={[styles.pointButton, styles.pointButtonMe]}
                onPress={() => recordPoint('me')}
              >
                <Text style={styles.pointButtonText}>Me</Text>
              </TouchableOpacity>

              <TouchableOpacity
                style={[styles.pointButton, styles.pointButtonLet]}
                onPress={() => recordPoint('me', true)}
              >
                <Text style={styles.pointButtonText}>Let</Text>
              </TouchableOpacity>

              <TouchableOpacity
                style={[styles.pointButton, styles.pointButtonOpponent]}
                onPress={() => recordPoint('opponent')}
              >
                <Text style={styles.pointButtonText}>Opponent</Text>
              </TouchableOpacity>
            </View>

            {/* Undo Button */}
            <TouchableOpacity
              style={styles.undoButton}
              onPress={handleUndoPoint}
              disabled={points.length === 0}
            >
              <Text style={styles.undoButtonText}>
                ↶ Undo Last Point ({points.length} recorded)
              </Text>
            </TouchableOpacity>

            {/* Next Game Button */}
            <TouchableOpacity
              style={styles.nextGameButton}
              onPress={handleNextGame}
            >
              <Text style={styles.nextGameButtonText}>
                Next Game →
              </Text>
            </TouchableOpacity>
          </View>
        )}

        {/* Tennis/Padel Score Tracking */}
        {session.session_type === 'match' && isTennisRegular && (
          <View style={styles.scoreCard}>
            <Text style={styles.scoreTitle}>
              Set {tennisCurrentSet} {tennisInTiebreak ? '- Tiebreaker' : `- Game ${tennisGamesMe + tennisGamesOpponent + 1}`}
            </Text>

            {/* Set Scores */}
            {tennisSetScores.length > 0 && (
              <View style={styles.tennisSetScoresContainer}>
                <Text style={styles.tennisSetScoresLabel}>Completed Sets:</Text>
                <Text style={styles.tennisSetScoresText}>{formatSetScores(tennisSetScores)}</Text>
              </View>
            )}

            {/* Current Set Games */}
            <View style={styles.tennisCurrentSetContainer}>
              <Text style={styles.tennisCurrentSetLabel}>Current Set:</Text>
              <Text style={styles.tennisCurrentSetScore}>{tennisGamesMe} - {tennisGamesOpponent}</Text>
            </View>

            {/* Current Game/Tiebreak Score */}
            <View style={styles.tennisGameScoreContainer}>
              <Text style={styles.tennisGameScoreLabel}>
                {tennisInTiebreak ? 'Tiebreak Score:' : 'Current Game:'}
              </Text>
              <View style={styles.tennisGameScoreDisplay}>
                {tennisInTiebreak ? (
                  <>
                    <Text style={styles.tennisGameScore}>{tennisTiebreakPointsMe} - {tennisTiebreakPointsOpponent}</Text>
                  </>
                ) : (
                  <>
                    <Text style={styles.tennisGameScore}>
                      {getTennisGameScore(tennisGamePointsMe, tennisGamePointsOpponent).me} - {getTennisGameScore(tennisGamePointsMe, tennisGamePointsOpponent).opponent}
                    </Text>
                  </>
                )}
              </View>
            </View>

            {/* Point Recording Buttons */}
            <Text style={styles.pointButtonsLabel}>Record Point:</Text>
            <View style={styles.pointButtonsRow}>
              <TouchableOpacity
                style={[styles.pointButton, styles.pointButtonMe]}
                onPress={() => recordTennisPoint('me')}
              >
                <Text style={styles.pointButtonText}>Me</Text>
              </TouchableOpacity>

              <TouchableOpacity
                style={[styles.pointButton, styles.pointButtonOpponent]}
                onPress={() => recordTennisPoint('opponent')}
              >
                <Text style={styles.pointButtonText}>Opponent</Text>
              </TouchableOpacity>
            </View>
          </View>
        )}

        {/* Action Buttons */}
        <View style={styles.actions}>
          <TouchableOpacity
            style={[styles.actionButton, styles.pauseButton]}
            onPress={handlePauseResume}
          >
            <Text style={styles.actionButtonText}>
              {isPaused ? '▶️ Resume' : '⏸️ Pause'}
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.actionButton, styles.endButton]}
            onPress={handleEndSession}
          >
            <Text style={styles.actionButtonText}>⏹️ End Session</Text>
          </TouchableOpacity>
        </View>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  content: {
    padding: 20,
  },
  infoCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 20,
    marginBottom: 20,
    alignItems: 'center',
  },
  sportLabel: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#007AFF',
    marginBottom: 8,
  },
  sessionType: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 8,
  },
  sessionId: {
    fontSize: 11,
    color: '#666',
    fontFamily: Platform.OS === 'ios' ? 'Courier' : 'monospace',
    marginTop: 8,
    paddingTop: 8,
    borderTopWidth: 1,
    borderTopColor: '#eee',
  },
  authToken: {
    fontSize: 9,
    color: '#999',
    fontFamily: Platform.OS === 'ios' ? 'Courier' : 'monospace',
    marginTop: 4,
  },
  refreshButton: {
    backgroundColor: '#28A745',
    borderRadius: 12,
    padding: 15,
    marginBottom: 20,
    alignItems: 'center',
  },
  refreshButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  timerCard: {
    backgroundColor: '#007AFF',
    borderRadius: 12,
    padding: 30,
    marginBottom: 20,
    alignItems: 'center',
  },
  timerLabel: {
    fontSize: 14,
    color: '#fff',
    opacity: 0.8,
    marginBottom: 10,
  },
  timerDisplay: {
    fontSize: 56,
    fontWeight: 'bold',
    color: '#fff',
    fontFamily: Platform.OS === 'ios' ? 'Courier' : 'monospace',
  },
  statusBadge: {
    backgroundColor: '#4CAF50',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 12,
    marginTop: 10,
  },
  pausedBadge: {
    backgroundColor: '#FF9800',
  },
  statusText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: 'bold',
  },
  statsCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 20,
    marginBottom: 20,
  },
  statsTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 15,
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  statItem: {
    width: '48%',
    alignItems: 'center',
    marginBottom: 15,
  },
  statValue: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#007AFF',
    marginBottom: 5,
  },
  statLabel: {
    fontSize: 12,
    color: '#999',
  },
  statsNote: {
    fontSize: 12,
    color: '#999',
    textAlign: 'center',
    fontStyle: 'italic',
    marginTop: 10,
  },
  actions: {
    marginBottom: 20,
  },
  actionButton: {
    borderRadius: 8,
    padding: 16,
    alignItems: 'center',
    marginBottom: 12,
  },
  pauseButton: {
    backgroundColor: '#FF9800',
  },
  endButton: {
    backgroundColor: '#dc3545',
  },
  actionButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  scoreCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 20,
    marginBottom: 20,
  },
  scoreTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 15,
    textAlign: 'center',
  },
  scoreDisplay: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 20,
    marginBottom: 20,
    backgroundColor: '#f8f8f8',
    borderRadius: 8,
  },
  scorePlayerSection: {
    alignItems: 'center',
    flex: 1,
  },
  scorePlayerLabel: {
    fontSize: 14,
    color: '#999',
    marginBottom: 8,
  },
  scorePlayerValue: {
    fontSize: 48,
    fontWeight: 'bold',
    color: '#007AFF',
  },
  scoreDivider: {
    fontSize: 36,
    color: '#ddd',
    marginHorizontal: 20,
  },
  pointButtonsLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: '#666',
    marginBottom: 10,
  },
  pointButtonsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 15,
  },
  pointButton: {
    flex: 1,
    paddingVertical: 16,
    borderRadius: 8,
    alignItems: 'center',
    marginHorizontal: 5,
  },
  pointButtonMe: {
    backgroundColor: '#4CAF50',
  },
  pointButtonLet: {
    backgroundColor: '#FF9800',
  },
  pointButtonOpponent: {
    backgroundColor: '#F44336',
  },
  pointButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  undoButton: {
    backgroundColor: '#f0f0f0',
    borderRadius: 8,
    paddingVertical: 12,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#ddd',
  },
  undoButtonText: {
    color: '#666',
    fontSize: 14,
    fontWeight: '600',
  },
  nextGameButton: {
    backgroundColor: '#007AFF',
    borderRadius: 8,
    paddingVertical: 14,
    alignItems: 'center',
    marginTop: 10,
  },
  nextGameButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  // Tennis-specific styles
  tennisSetScoresContainer: {
    backgroundColor: '#f8f8f8',
    padding: 12,
    borderRadius: 8,
    marginBottom: 15,
  },
  tennisSetScoresLabel: {
    fontSize: 13,
    color: '#666',
    marginBottom: 4,
  },
  tennisSetScoresText: {
    fontSize: 16,
    color: '#333',
    fontWeight: 'bold',
    letterSpacing: 2,
  },
  tennisCurrentSetContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
    marginBottom: 15,
  },
  tennisCurrentSetLabel: {
    fontSize: 15,
    color: '#666',
    fontWeight: '600',
  },
  tennisCurrentSetScore: {
    fontSize: 24,
    color: '#007AFF',
    fontWeight: 'bold',
  },
  tennisGameScoreContainer: {
    marginBottom: 20,
  },
  tennisGameScoreLabel: {
    fontSize: 14,
    color: '#666',
    marginBottom: 8,
  },
  tennisGameScoreDisplay: {
    alignItems: 'center',
  },
  tennisGameScore: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#007AFF',
  },
});
