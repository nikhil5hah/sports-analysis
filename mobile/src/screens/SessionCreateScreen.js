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

export default function SessionCreateScreen({ navigation }) {
  const [sessionType, setSessionType] = useState('match');
  const [sport, setSport] = useState('squash');
  const [scoringSystem, setScoringSystem] = useState('american');
  const [scoringMode, setScoringMode] = useState('referee'); // 'player' | 'referee'
  const [opponentName, setOpponentName] = useState('');
  const [location, setLocation] = useState('');
  const [loading, setLoading] = useState(false);

  const handleCreateSession = async () => {
    setLoading(true);

    try {
      const sessionData = {
        session_type: sessionType,
        sport: sport,
        scoring_system: scoringSystem,
      };

      // Add optional fields if provided
      if (opponentName.trim()) {
        sessionData.opponent_name = opponentName.trim();
      }
      if (location.trim()) {
        sessionData.location = location.trim();
      }

      // Add scoring mode to metadata (for matches only)
      if (sessionType === 'match') {
        sessionData.metadata = JSON.stringify({
          scoring_mode: scoringMode,
        });
      }

      const session = await apiClient.createSession(sessionData);

      if (Platform.OS === 'web') {
        const choice = window.confirm(
          'Session created successfully!\n\nClick OK to start the session now, or Cancel to view all sessions.'
        );
        if (choice) {
          navigation.replace('ActiveSession', { session });
        } else {
          navigation.replace('SessionList');
        }
      } else {
        Alert.alert(
          'Session Created!',
          'Your session has been created successfully.',
          [
            {
              text: 'Start Session',
              onPress: () => navigation.replace('ActiveSession', { session }),
            },
            {
              text: 'View Sessions',
              onPress: () => navigation.replace('SessionList'),
            },
          ]
        );
      }
    } catch (error) {
      if (Platform.OS === 'web') {
        alert('Error: ' + error.message);
      } else {
        Alert.alert('Error', error.message);
      }
    } finally {
      setLoading(false);
    }
  };

  const OptionButton = ({ label, value, selectedValue, onPress }) => (
    <TouchableOpacity
      style={[
        styles.optionButton,
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
          <View style={styles.optionRow}>
            <OptionButton
              label="Squash"
              value="squash"
              selectedValue={sport}
              onPress={() => setSport('squash')}
            />
            <OptionButton
              label="Tennis"
              value="tennis"
              selectedValue={sport}
              onPress={() => setSport('tennis')}
            />
          </View>
          <View style={styles.optionRow}>
            <OptionButton
              label="Badminton"
              value="badminton"
              selectedValue={sport}
              onPress={() => setSport('badminton')}
            />
            <OptionButton
              label="Table Tennis"
              value="table_tennis"
              selectedValue={sport}
              onPress={() => setSport('table_tennis')}
            />
          </View>
          <View style={styles.optionRow}>
            <OptionButton
              label="Padel"
              value="padel"
              selectedValue={sport}
              onPress={() => setSport('padel')}
            />
          </View>
        </View>

        {/* Scoring System (only for matches) */}
        {sessionType === 'match' && (
          <View style={styles.section}>
            <Text style={styles.label}>Scoring System</Text>
            <View style={styles.optionRow}>
              <OptionButton
                label="American (PARS)"
                value="american"
                selectedValue={scoringSystem}
                onPress={() => setScoringSystem('american')}
              />
              <OptionButton
                label="English"
                value="english"
                selectedValue={scoringSystem}
                onPress={() => setScoringSystem('english')}
              />
            </View>
          </View>
        )}

        {/* Scoring Mode (only for matches) */}
        {sessionType === 'match' && (
          <View style={styles.section}>
            <Text style={styles.label}>Scoring Mode</Text>
            <Text style={styles.helperText}>
              Choose how you'll track the score during the match
            </Text>

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
                  Player Mode
                </Text>
              </View>
              <Text style={styles.modeDescription}>
                I'll wear the watch and track my own score hands-free during play
              </Text>
              <Text style={styles.modeNote}>
                ⌚ Requires smartwatch (Apple Watch / Pixel Watch / Galaxy Watch)
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
                  Referee Mode
                </Text>
              </View>
              <Text style={styles.modeDescription}>
                A referee or coach will track the score using this phone
              </Text>
              <Text style={styles.modeNote}>
                📱 Best for competitive matches and coaching
              </Text>
            </TouchableOpacity>
          </View>
        )}

        {/* Opponent Name (optional, only for matches) */}
        {sessionType === 'match' && (
          <View style={styles.section}>
            <Text style={styles.label}>Opponent Name (Optional)</Text>
            <TextInput
              style={styles.input}
              placeholder="Enter opponent's name"
              placeholderTextColor="#999"
              value={opponentName}
              onChangeText={setOpponentName}
              autoCapitalize="words"
              editable={!loading}
            />
          </View>
        )}

        {/* Location (optional) */}
        <View style={styles.section}>
          <Text style={styles.label}>Location (Optional)</Text>
          <TextInput
            style={styles.input}
            placeholder="Enter location"
            placeholderTextColor="#999"
            value={location}
            onChangeText={setLocation}
            autoCapitalize="words"
            editable={!loading}
          />
        </View>

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
    backgroundColor: '#f5f5f5',
  },
  content: {
    padding: 20,
    paddingBottom: 40,
  },
  header: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 30,
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
  modeCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
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
    marginBottom: 8,
  },
  radioOuter: {
    width: 20,
    height: 20,
    borderRadius: 10,
    borderWidth: 2,
    borderColor: '#ddd',
    marginRight: 12,
    justifyContent: 'center',
    alignItems: 'center',
  },
  radioOuterSelected: {
    borderColor: '#007AFF',
  },
  radioInner: {
    width: 10,
    height: 10,
    borderRadius: 5,
    backgroundColor: '#007AFF',
  },
  modeTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
  },
  modeTitleSelected: {
    color: '#007AFF',
  },
  modeDescription: {
    fontSize: 14,
    color: '#666',
    marginBottom: 8,
    lineHeight: 20,
  },
  modeNote: {
    fontSize: 12,
    color: '#999',
    fontStyle: 'italic',
  },
  optionRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginBottom: 10,
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
  optionButtonSelected: {
    backgroundColor: '#007AFF',
    borderColor: '#007AFF',
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
    backgroundColor: '#007AFF',
    borderRadius: 8,
    padding: 15,
    alignItems: 'center',
    marginTop: 10,
  },
  createButtonDisabled: {
    backgroundColor: '#99c7ff',
  },
  createButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
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
