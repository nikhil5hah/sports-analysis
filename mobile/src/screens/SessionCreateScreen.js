import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  ActivityIndicator,
  Alert,
  Platform,
} from 'react-native';
import apiClient from '../api/client';
import { COLORS } from '../constants/colors';

export default function SessionCreateScreen({ navigation }) {
  const [sessionType, setSessionType] = useState('match');
  const [sport, setSport] = useState('squash');
  const [scoringSystem, setScoringSystem] = useState('par_11');
  const [scoringMode, setScoringMode] = useState('player'); // 'player' | 'referee'
  const [bestOfGames, setBestOfGames] = useState(1); // 1, 3, 5, or 7 (for table tennis)
  const [loading, setLoading] = useState(false);

  // Update scoring system when sport changes
  React.useEffect(() => {
    if (sport === 'squash') {
      setScoringSystem('par_11');
    } else if (sport === 'badminton') {
      setScoringSystem('par_15');
    } else if (sport === 'table_tennis') {
      setScoringSystem('par_11');
    } else if (sport === 'tennis' || sport === 'padel') {
      setScoringSystem('regular');
    }
  }, [sport]);

  const handleCreateSession = async () => {
    setLoading(true);

    try {
      const sessionData = {
        session_type: sessionType,
        sport: sport,
        scoring_system: scoringSystem,
      };

      // Add scoring mode and best-of-games to metadata (for matches only)
      if (sessionType === 'match') {
        const metadata = {
          scoring_mode: scoringMode,
          best_of_games: bestOfGames,
        };

        sessionData.metadata = JSON.stringify(metadata);
      }

      const session = await apiClient.createSession(sessionData);

      if (Platform.OS === 'web') {
        const choice = window.confirm(
          'Session created successfully!\n\nClick OK to start the session now, or Cancel to view all sessions.'
        );
        if (choice) {
          navigation.navigate('ActiveSession', { session });
        } else {
          navigation.navigate('SessionList');
        }
      } else {
        Alert.alert(
          'Session Created!',
          'Your session has been created successfully.',
          [
            {
              text: 'Start Session',
              onPress: () => navigation.navigate('ActiveSession', { session }),
            },
            {
              text: 'View Sessions',
              onPress: () => navigation.navigate('SessionList'),
            },
          ]
        );
      }
    } catch (error) {
      const errorMessage = error.message || 'Failed to create session. Please try again.';
      if (Platform.OS === 'web') {
        alert('Error: ' + errorMessage);
      } else {
        Alert.alert('Error', errorMessage);
      }
    } finally {
      setLoading(false);
    }
  };

  const OptionButton = ({ label, value, selectedValue, onPress, compact }) => (
    <TouchableOpacity
      style={[
        styles.optionButton,
        compact && styles.optionButtonCompact,
        selectedValue === value && styles.optionButtonSelected,
      ]}
      onPress={onPress}
    >
      <Text
        style={[
          styles.optionButtonText,
          selectedValue === value && styles.optionButtonTextSelected,
        ]}
      >
        {label}
      </Text>
    </TouchableOpacity>
  );

  return (
    <ScrollView style={styles.container}>
      <View style={styles.content}>
        <Text style={styles.header}>Create New Session</Text>

        {/* Description */}
        <View style={styles.descriptionBox}>
          <Text style={styles.descriptionText}>
            Start tracking your match or training session. Record scores in real-time,
            track your performance metrics, and analyze your game after completion.
          </Text>
        </View>

        {/* Session Type */}
        <View style={styles.section}>
          <Text style={styles.label}>Session Type</Text>
          <View style={styles.optionRow}>
            <OptionButton
              label="Match"
              value="match"
              selectedValue={sessionType}
              onPress={() => setSessionType('match')}
            />
            <OptionButton
              label="Training"
              value="training"
              selectedValue={sessionType}
              onPress={() => setSessionType('training')}
            />
          </View>
        </View>

        {/* Sport */}
        <View style={styles.section}>
          <Text style={styles.label}>Sport</Text>
          <View style={styles.sportRow}>
            <OptionButton
              label="Squash"
              value="squash"
              selectedValue={sport}
              onPress={() => setSport('squash')}
              compact
            />
            <OptionButton
              label="Tennis"
              value="tennis"
              selectedValue={sport}
              onPress={() => setSport('tennis')}
              compact
            />
            <OptionButton
              label="Badminton"
              value="badminton"
              selectedValue={sport}
              onPress={() => setSport('badminton')}
              compact
            />
            <OptionButton
              label="Table Tennis"
              value="table_tennis"
              selectedValue={sport}
              onPress={() => setSport('table_tennis')}
              compact
            />
            <OptionButton
              label="Padel"
              value="padel"
              selectedValue={sport}
              onPress={() => setSport('padel')}
              compact
            />
          </View>
        </View>

        {/* Scoring System (only for matches) */}
        {sessionType === 'match' && (
          <View style={styles.section}>
            <Text style={styles.label}>Scoring System</Text>
            <View style={styles.optionRow}>
              {sport === 'squash' && (
                <>
                  <OptionButton
                    label="PAR 11"
                    value="par_11"
                    selectedValue={scoringSystem}
                    onPress={() => setScoringSystem('par_11')}
                  />
                  <OptionButton
                    label="English"
                    value="english"
                    selectedValue={scoringSystem}
                    onPress={() => setScoringSystem('english')}
                  />
                </>
              )}
              {sport === 'badminton' && (
                <>
                  <OptionButton
                    label="PAR 15"
                    value="par_15"
                    selectedValue={scoringSystem}
                    onPress={() => setScoringSystem('par_15')}
                  />
                  <OptionButton
                    label="PAR 21"
                    value="par_21"
                    selectedValue={scoringSystem}
                    onPress={() => setScoringSystem('par_21')}
                  />
                </>
              )}
              {sport === 'table_tennis' && (
                <>
                  <OptionButton
                    label="PAR 11"
                    value="par_11"
                    selectedValue={scoringSystem}
                    onPress={() => setScoringSystem('par_11')}
                  />
                  <OptionButton
                    label="PAR 21"
                    value="par_21"
                    selectedValue={scoringSystem}
                    onPress={() => setScoringSystem('par_21')}
                  />
                </>
              )}
              {(sport === 'tennis' || sport === 'padel') && (
                <>
                  <OptionButton
                    label="Regular"
                    value="regular"
                    selectedValue={scoringSystem}
                    onPress={() => setScoringSystem('regular')}
                  />
                  <OptionButton
                    label="Tie-Break"
                    value="tiebreak"
                    selectedValue={scoringSystem}
                    onPress={() => setScoringSystem('tiebreak')}
                  />
                </>
              )}
            </View>
          </View>
        )}

        {/* Best of Games (for all sports) */}
        {sessionType === 'match' && (
          <View style={styles.section}>
            <Text style={styles.label}>Match Format</Text>
            <View style={styles.optionRow}>
              <OptionButton
                label="1 Game"
                value={1}
                selectedValue={bestOfGames}
                onPress={() => setBestOfGames(1)}
              />
              <OptionButton
                label="Best of 3"
                value={3}
                selectedValue={bestOfGames}
                onPress={() => setBestOfGames(3)}
              />
              <OptionButton
                label="Best of 5"
                value={5}
                selectedValue={bestOfGames}
                onPress={() => setBestOfGames(5)}
              />
              {sport === 'table_tennis' && (
                <OptionButton
                  label="Best of 7"
                  value={7}
                  selectedValue={bestOfGames}
                  onPress={() => setBestOfGames(7)}
                />
              )}
            </View>
          </View>
        )}

        {/* Scoring Mode (only for matches) */}
        {sessionType === 'match' && (
          <View style={styles.section}>
            <Text style={styles.label}>Scoring Mode</Text>
            <View style={styles.modeRow}>
              <TouchableOpacity
                style={[
                  styles.modeCard,
                  scoringMode === 'player' && styles.modeCardSelected,
                ]}
                onPress={() => setScoringMode('player')}
              >
                <View style={styles.modeHeader}>
                  <View style={[
                    styles.radioOuter,
                    scoringMode === 'player' && styles.radioOuterSelected,
                  ]}>
                    {scoringMode === 'player' && <View style={styles.radioInner} />}
                  </View>
                  <Text style={[
                    styles.modeTitle,
                    scoringMode === 'player' && styles.modeTitleSelected,
                  ]}>
                    Player
                  </Text>
                </View>
                <Text style={styles.modeDescription}>
                  ⌚ Track with watch
                </Text>
              </TouchableOpacity>

              <TouchableOpacity
                style={[
                  styles.modeCard,
                  scoringMode === 'referee' && styles.modeCardSelected,
                ]}
                onPress={() => setScoringMode('referee')}
              >
                <View style={styles.modeHeader}>
                  <View style={[
                    styles.radioOuter,
                    scoringMode === 'referee' && styles.radioOuterSelected,
                  ]}>
                    {scoringMode === 'referee' && <View style={styles.radioInner} />}
                  </View>
                  <Text style={[
                    styles.modeTitle,
                    scoringMode === 'referee' && styles.modeTitleSelected,
                  ]}>
                    Referee
                  </Text>
                </View>
                <Text style={styles.modeDescription}>
                  📱 Track with phone
                </Text>
              </TouchableOpacity>
            </View>
          </View>
        )}

        {/* Create Button */}
        <TouchableOpacity
          style={[styles.createButton, loading && styles.createButtonDisabled]}
          onPress={handleCreateSession}
          disabled={loading}
        >
          {loading ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <Text style={styles.createButtonText}>Create Session</Text>
          )}
        </TouchableOpacity>

        {/* Cancel Button */}
        <TouchableOpacity
          style={styles.cancelButton}
          onPress={() => navigation.goBack()}
          disabled={loading}
        >
          <Text style={styles.cancelButtonText}>Cancel</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.background,
  },
  content: {
    padding: 20,
    paddingBottom: 40,
  },
  header: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 20,
  },
  descriptionBox: {
    backgroundColor: '#e3f2fd',
    borderRadius: 12,
    padding: 16,
    marginBottom: 25,
    borderLeftWidth: 4,
    borderLeftColor: '#007AFF',
  },
  descriptionText: {
    fontSize: 15,
    color: '#1565c0',
    lineHeight: 22,
  },
  section: {
    marginBottom: 25,
  },
  label: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 10,
  },
  helperText: {
    fontSize: 14,
    color: '#666',
    marginBottom: 15,
    lineHeight: 20,
  },
  modeRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    gap: 10,
  },
  modeCard: {
    flex: 1,
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 12,
    borderWidth: 2,
    borderColor: '#ddd',
  },
  modeCardSelected: {
    borderColor: '#007AFF',
    backgroundColor: '#f0f7ff',
  },
  modeHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 6,
  },
  radioOuter: {
    width: 18,
    height: 18,
    borderRadius: 9,
    borderWidth: 2,
    borderColor: '#ddd',
    marginRight: 8,
    justifyContent: 'center',
    alignItems: 'center',
  },
  radioOuterSelected: {
    borderColor: '#007AFF',
  },
  radioInner: {
    width: 9,
    height: 9,
    borderRadius: 4.5,
    backgroundColor: '#007AFF',
  },
  modeTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#333',
  },
  modeTitleSelected: {
    color: '#007AFF',
  },
  modeDescription: {
    fontSize: 13,
    color: '#666',
    lineHeight: 18,
  },
  optionRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginBottom: 10,
  },
  sportRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'flex-start',
  },
  optionButton: {
    backgroundColor: '#fff',
    borderRadius: 8,
    padding: 12,
    marginRight: 10,
    marginBottom: 10,
    borderWidth: 2,
    borderColor: '#ddd',
    minWidth: 100,
    alignItems: 'center',
  },
  optionButtonCompact: {
    padding: 8,
    minWidth: 70,
    marginRight: 6,
  },
  optionButtonSelected: {
    backgroundColor: COLORS.buttonPrimary,
    borderColor: COLORS.buttonPrimary,
  },
  optionButtonText: {
    fontSize: 14,
    color: '#333',
    fontWeight: '500',
  },
  optionButtonTextSelected: {
    color: '#fff',
    fontWeight: '600',
  },
  input: {
    backgroundColor: '#fff',
    borderRadius: 8,
    padding: 15,
    fontSize: 16,
    borderWidth: 1,
    borderColor: '#ddd',
  },
  createButton: {
    backgroundColor: COLORS.buttonPrimary,
    borderRadius: 12,
    padding: 18,
    alignItems: 'center',
    marginTop: 10,
    shadowColor: COLORS.buttonPrimary,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.4,
    shadowRadius: 8,
    elevation: 5,
  },
  createButtonDisabled: {
    backgroundColor: COLORS.buttonDisabled,
    opacity: 0.7,
  },
  createButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
    textTransform: 'uppercase',
    letterSpacing: 1,
  },
  cancelButton: {
    backgroundColor: '#fff',
    borderRadius: 8,
    padding: 15,
    alignItems: 'center',
    marginTop: 10,
    borderWidth: 1,
    borderColor: '#ddd',
  },
  cancelButtonText: {
    color: '#666',
    fontSize: 16,
    fontWeight: '600',
  },
});
