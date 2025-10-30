import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  ActivityIndicator,
  TouchableOpacity,
  Alert,
  Platform,
} from 'react-native';
import apiClient from '../api/client';

export default function SessionDetailsScreen({ navigation, route }) {
  const { sessionId } = route.params;
  const [session, setSession] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSessionDetails();
  }, [sessionId]);

  const fetchSessionDetails = async () => {
    try {
      const data = await apiClient.getSession(sessionId);
      setSession(data);
    } catch (error) {
      Alert.alert('Error', error.message);
      navigation.goBack();
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getDuration = (startTime, endTime) => {
    if (!endTime) return 'In progress';

    const start = new Date(startTime);
    const end = new Date(endTime);
    const durationMs = end - start;
    const minutes = Math.floor(durationMs / 60000);

    if (minutes < 60) {
      return `${minutes} minutes`;
    }

    const hours = Math.floor(minutes / 60);
    const remainingMinutes = minutes % 60;
    return `${hours}h ${remainingMinutes}m`;
  };

  const handleDelete = async () => {
    // Use native confirm on web, Alert.alert on mobile
    if (Platform.OS === 'web') {
      const confirmed = window.confirm(
        'Are you sure you want to delete this session? This action cannot be undone.'
      );

      if (confirmed) {
        try {
          await apiClient.deleteSession(sessionId);
          alert('Session deleted successfully');
          navigation.navigate('SessionList');
        } catch (error) {
          alert('Error: ' + error.message);
        }
      }
    } else {
      Alert.alert(
        'Delete Session',
        'Are you sure you want to delete this session? This action cannot be undone.',
        [
          {
            text: 'Cancel',
            style: 'cancel',
          },
          {
            text: 'Delete',
            style: 'destructive',
            onPress: async () => {
              try {
                await apiClient.deleteSession(sessionId);
                Alert.alert('Success', 'Session deleted successfully', [
                  {
                    text: 'OK',
                    onPress: () => navigation.navigate('SessionList'),
                  },
                ]);
              } catch (error) {
                Alert.alert('Error', error.message);
              }
            },
          },
        ]
      );
    }
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#007AFF" />
      </View>
    );
  }

  if (!session) {
    return (
      <View style={styles.errorContainer}>
        <Text style={styles.errorText}>Session not found</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      <View style={styles.content}>
        {/* Header */}
        <View style={styles.headerCard}>
          <Text style={styles.sportLabel}>{session.sport?.toUpperCase() || 'UNKNOWN'}</Text>
          <Text style={styles.sessionType}>
            {session.session_type === 'match' ? '🎯 Match' : '💪 Training Session'}
          </Text>
          {session.opponent_name && (
            <Text style={styles.opponent}>vs {session.opponent_name}</Text>
          )}
          <View style={styles.statusBadge}>
            <Text style={styles.statusText}>{session.status?.toUpperCase() || 'UNKNOWN'}</Text>
          </View>
        </View>

        {/* Time & Location */}
        <View style={styles.detailsCard}>
          <Text style={styles.sectionTitle}>Session Details</Text>

          <View style={styles.detailRow}>
            <Text style={styles.detailLabel}>Started:</Text>
            <Text style={styles.detailValue}>{formatDate(session.start_time)}</Text>
          </View>

          {session.end_time && (
            <View style={styles.detailRow}>
              <Text style={styles.detailLabel}>Ended:</Text>
              <Text style={styles.detailValue}>{formatDate(session.end_time)}</Text>
            </View>
          )}

          <View style={styles.detailRow}>
            <Text style={styles.detailLabel}>Duration:</Text>
            <Text style={styles.detailValue}>
              {getDuration(session.start_time, session.end_time)}
            </Text>
          </View>

          {session.location && (
            <View style={styles.detailRow}>
              <Text style={styles.detailLabel}>Location:</Text>
              <Text style={styles.detailValue}>📍 {session.location}</Text>
            </View>
          )}

          {session.session_type === 'match' && session.scoring_system && (
            <View style={styles.detailRow}>
              <Text style={styles.detailLabel}>Scoring:</Text>
              <Text style={styles.detailValue}>
                {session.scoring_system === 'american' ? 'American (PARS)' : 'English'}
              </Text>
            </View>
          )}
        </View>

        {/* Score (if match) */}
        {session.session_type === 'match' && (
          <View style={styles.detailsCard}>
            <Text style={styles.sectionTitle}>Final Score</Text>
            <View style={styles.scoreRow}>
              <View style={styles.scoreColumn}>
                <Text style={styles.scoreLabel}>Me</Text>
                <Text style={styles.scoreValue}>
                  {session.final_score_me !== null && session.final_score_me !== undefined ? session.final_score_me : '--'}
                </Text>
              </View>
              <Text style={styles.scoreDivider}>-</Text>
              <View style={styles.scoreColumn}>
                <Text style={styles.scoreLabel}>Opponent</Text>
                <Text style={styles.scoreValue}>
                  {session.final_score_opponent !== null && session.final_score_opponent !== undefined ? session.final_score_opponent : '--'}
                </Text>
              </View>
            </View>
            {session.metadata && JSON.parse(session.metadata || '{}').game_scores && (
              <View style={styles.gameScoresSection}>
                <Text style={styles.gameScoresLabel}>Game Scores:</Text>
                <Text style={styles.gameScoresValue}>
                  {JSON.parse(session.metadata).game_scores}
                </Text>
              </View>
            )}
            {session.total_points > 0 && (
              <Text style={styles.statsText}>Total Points: {session.total_points}</Text>
            )}
            {session.total_lets > 0 && (
              <Text style={styles.statsText}>Lets: {session.total_lets}</Text>
            )}
          </View>
        )}

        {/* Stats Placeholder */}
        <View style={styles.detailsCard}>
          <Text style={styles.sectionTitle}>Performance Stats</Text>
          <View style={styles.statsGrid}>
            <View style={styles.statItem}>
              <Text style={styles.statValue}>--</Text>
              <Text style={styles.statLabel}>Avg Heart Rate</Text>
            </View>
            <View style={styles.statItem}>
              <Text style={styles.statValue}>--</Text>
              <Text style={styles.statLabel}>Max Heart Rate</Text>
            </View>
            <View style={styles.statItem}>
              <Text style={styles.statValue}>--</Text>
              <Text style={styles.statLabel}>Calories</Text>
            </View>
            <View style={styles.statItem}>
              <Text style={styles.statValue}>--</Text>
              <Text style={styles.statLabel}>Distance</Text>
            </View>
          </View>
          <Text style={styles.statsNote}>
            Stats will be available with smartwatch integration
          </Text>
        </View>

        {/* Notes */}
        {session.notes && (
          <View style={styles.detailsCard}>
            <Text style={styles.sectionTitle}>Notes</Text>
            <Text style={styles.notesText}>{session.notes}</Text>
          </View>
        )}

        {/* Actions */}
        <View style={styles.actions}>
          <TouchableOpacity
            style={styles.deleteButton}
            onPress={handleDelete}
          >
            <Text style={styles.deleteButtonText}>Delete Session</Text>
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
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f5f5f5',
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  errorText: {
    fontSize: 16,
    color: '#666',
  },
  content: {
    padding: 20,
  },
  headerCard: {
    backgroundColor: '#007AFF',
    borderRadius: 12,
    padding: 24,
    marginBottom: 20,
    alignItems: 'center',
  },
  sportLabel: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#fff',
    opacity: 0.9,
    marginBottom: 8,
  },
  sessionType: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 8,
  },
  opponent: {
    fontSize: 18,
    color: '#fff',
    marginBottom: 12,
  },
  statusBadge: {
    backgroundColor: 'rgba(255,255,255,0.2)',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 12,
  },
  statusText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: 'bold',
  },
  detailsCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 20,
    marginBottom: 20,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 15,
  },
  detailRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 12,
    paddingBottom: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  detailLabel: {
    fontSize: 14,
    color: '#999',
    fontWeight: '600',
  },
  detailValue: {
    fontSize: 14,
    color: '#333',
    flex: 1,
    textAlign: 'right',
  },
  scoreRow: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 20,
  },
  scoreColumn: {
    alignItems: 'center',
    flex: 1,
  },
  scoreLabel: {
    fontSize: 14,
    color: '#999',
    marginBottom: 8,
  },
  scoreValue: {
    fontSize: 48,
    fontWeight: 'bold',
    color: '#007AFF',
  },
  scoreDivider: {
    fontSize: 36,
    color: '#ddd',
    marginHorizontal: 20,
  },
  letsText: {
    fontSize: 14,
    color: '#999',
    textAlign: 'center',
    marginTop: 10,
  },
  gameScoresSection: {
    marginTop: 20,
    paddingTop: 20,
    borderTopWidth: 1,
    borderTopColor: '#f0f0f0',
  },
  gameScoresLabel: {
    fontSize: 14,
    color: '#999',
    fontWeight: '600',
    marginBottom: 8,
    textAlign: 'center',
  },
  gameScoresValue: {
    fontSize: 18,
    color: '#333',
    fontWeight: 'bold',
    textAlign: 'center',
    letterSpacing: 2,
  },
  statsText: {
    fontSize: 14,
    color: '#666',
    textAlign: 'center',
    marginTop: 8,
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    marginBottom: 15,
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
    textAlign: 'center',
  },
  statsNote: {
    fontSize: 12,
    color: '#999',
    textAlign: 'center',
    fontStyle: 'italic',
  },
  notesText: {
    fontSize: 14,
    color: '#666',
    lineHeight: 22,
  },
  actions: {
    marginTop: 10,
    marginBottom: 20,
  },
  deleteButton: {
    backgroundColor: '#dc3545',
    borderRadius: 8,
    padding: 15,
    alignItems: 'center',
  },
  deleteButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
});
