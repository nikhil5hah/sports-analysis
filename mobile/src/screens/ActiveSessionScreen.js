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
import apiClient from '../api/client';

export default function ActiveSessionScreen({ navigation, route }) {
  const { session } = route.params;
  const [elapsedTime, setElapsedTime] = useState(0);
  const [isPaused, setIsPaused] = useState(false);

  // Score tracking state (for matches only)
  const [scoreMe, setScoreMe] = useState(0);
  const [scoreOpponent, setScoreOpponent] = useState(0);
  const [gameNumber, setGameNumber] = useState(1);
  const [points, setPoints] = useState([]);

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
      console.error('Error loading points:', error);
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
        is_let: isLet ? 'true' : 'false',
      };

      const newPoint = await apiClient.recordPoint(session.session_id, pointData);
      setPoints([...points, newPoint]);
      setScoreMe(newScoreMe);
      setScoreOpponent(newScoreOpponent);
    } catch (error) {
      if (Platform.OS === 'web') {
        alert('Error recording point: ' + error.message);
      } else {
        Alert.alert('Error', error.message);
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
      if (Platform.OS === 'web') {
        alert('Error undoing point: ' + error.message);
      } else {
        Alert.alert('Error', error.message);
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

  const formatTime = (seconds) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;

    if (hours > 0) {
      return `${hours}:${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
    }
    return `${minutes}:${String(secs).padStart(2, '0')}`;
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
          if (viewDetails) {
            navigation.replace('SessionDetails', {
              sessionId: session.session_id,
            });
          } else {
            navigation.replace('SessionList');
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
                      onPress: () =>
                        navigation.replace('SessionDetails', {
                          sessionId: session.session_id,
                        }),
                    },
                    {
                      text: 'View Sessions',
                      onPress: () => navigation.replace('SessionList'),
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
          <Text style={styles.sportLabel}>{session.sport.toUpperCase()}</Text>
          <Text style={styles.sessionType}>
            {session.session_type === 'match' ? 'Match' : 'Training Session'}
          </Text>
          {session.opponent_name && (
            <Text style={styles.opponent}>vs {session.opponent_name}</Text>
          )}
          {session.location && (
            <Text style={styles.location}>📍 {session.location}</Text>
          )}
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
        {session.session_type === 'match' && (
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

        {/* Info Box */}
        <View style={styles.infoBox}>
          <Text style={styles.infoTitle}>💡 Coming Soon</Text>
          <Text style={styles.infoText}>
            • Real-time heart rate tracking{'\n'}
            • Score tracking for matches{'\n'}
            • GPS tracking{'\n'}
            • Performance insights
          </Text>
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
  opponent: {
    fontSize: 18,
    color: '#666',
    marginBottom: 8,
  },
  location: {
    fontSize: 14,
    color: '#999',
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
  infoBox: {
    backgroundColor: '#e3f2fd',
    borderRadius: 12,
    padding: 16,
    borderWidth: 1,
    borderColor: '#90caf9',
  },
  infoTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#1976d2',
    marginBottom: 8,
  },
  infoText: {
    fontSize: 14,
    color: '#1565c0',
    lineHeight: 22,
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
});
