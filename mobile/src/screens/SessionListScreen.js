import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  FlatList,
  TouchableOpacity,
  StyleSheet,
  RefreshControl,
  ActivityIndicator,
} from 'react-native';
import apiClient from '../api/client';

export default function SessionListScreen({ navigation }) {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    fetchSessions();
  }, []);

  const fetchSessions = async () => {
    try {
      const data = await apiClient.getSessions();
      setSessions(data);
    } catch (error) {
      console.error('Error fetching sessions:', error);
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    await fetchSessions();
    setRefreshing(false);
  }, []);

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const options = {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    };
    return date.toLocaleDateString('en-US', options);
  };

  const getSessionDuration = (startTime, endTime) => {
    if (!endTime) return 'In progress';

    const start = new Date(startTime);
    const end = new Date(endTime);
    const durationMs = end - start;
    const minutes = Math.floor(durationMs / 60000);

    if (minutes < 60) {
      return `${minutes}m`;
    }

    const hours = Math.floor(minutes / 60);
    const remainingMinutes = minutes % 60;
    return `${hours}h ${remainingMinutes}m`;
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active':
        return '#4CAF50';
      case 'completed':
        return '#2196F3';
      case 'paused':
        return '#FF9800';
      default:
        return '#999';
    }
  };

  const renderSessionItem = ({ item }) => (
    <TouchableOpacity
      style={styles.sessionCard}
      onPress={() => {
        if (item.status === 'active') {
          navigation.navigate('ActiveSession', { session: item });
        } else {
          navigation.navigate('SessionDetails', { sessionId: item.session_id });
        }
      }}
    >
      <View style={styles.sessionHeader}>
        <View style={styles.sessionHeaderLeft}>
          <Text style={styles.sessionSport}>{item.sport.toUpperCase()}</Text>
          <View style={[styles.statusBadge, { backgroundColor: getStatusColor(item.status) }]}>
            <Text style={styles.statusText}>{item.status}</Text>
          </View>
        </View>
        <Text style={styles.sessionDate}>{formatDate(item.start_time)}</Text>
      </View>

      <View style={styles.sessionInfo}>
        <Text style={styles.sessionType}>
          {item.session_type === 'match' ? '🎯 Match' : '💪 Training'}
        </Text>
        {item.opponent_name && (
          <Text style={styles.sessionOpponent}>vs {item.opponent_name}</Text>
        )}
      </View>

      {item.session_type === 'match' && item.end_time && (item.final_score_me !== null || item.final_score_opponent !== null) && (
        <View style={styles.matchScoreContainer}>
          <Text style={styles.matchScore}>
            Result: {item.final_score_me || 0} - {item.final_score_opponent || 0}
          </Text>
          {item.metadata && JSON.parse(item.metadata || '{}').game_scores && (
            <Text style={styles.gameScores}>
              ({JSON.parse(item.metadata).game_scores})
            </Text>
          )}
        </View>
      )}

      {item.location && (
        <Text style={styles.sessionLocation}>📍 {item.location}</Text>
      )}

      <View style={styles.sessionFooter}>
        <Text style={styles.sessionDuration}>
          {getSessionDuration(item.start_time, item.end_time)}
        </Text>
        {item.session_type === 'match' && item.scoring_system && (
          <Text style={styles.sessionScoring}>
            {item.scoring_system === 'american' ? 'PARS' : 'English'}
          </Text>
        )}
      </View>
    </TouchableOpacity>
  );

  const renderEmptyState = () => (
    <View style={styles.emptyState}>
      <Text style={styles.emptyStateIcon}>🎾</Text>
      <Text style={styles.emptyStateTitle}>No Sessions Yet</Text>
      <Text style={styles.emptyStateText}>
        Create your first session to start tracking your performance!
      </Text>
      <TouchableOpacity
        style={styles.createButton}
        onPress={() => navigation.navigate('SessionCreate')}
      >
        <Text style={styles.createButtonText}>Create Session</Text>
      </TouchableOpacity>
    </View>
  );

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#007AFF" />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>My Sessions</Text>
        <TouchableOpacity
          style={styles.addButton}
          onPress={() => navigation.navigate('SessionCreate')}
        >
          <Text style={styles.addButtonText}>+ New</Text>
        </TouchableOpacity>
      </View>

      <FlatList
        data={sessions}
        renderItem={renderSessionItem}
        keyExtractor={(item) => item.session_id}
        contentContainerStyle={
          sessions.length === 0 ? styles.emptyContainer : styles.listContainer
        }
        ListEmptyComponent={renderEmptyState}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      />
    </View>
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
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#ddd',
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
  },
  addButton: {
    backgroundColor: '#007AFF',
    borderRadius: 8,
    paddingHorizontal: 16,
    paddingVertical: 8,
  },
  addButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  listContainer: {
    padding: 15,
  },
  emptyContainer: {
    flexGrow: 1,
  },
  sessionCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  sessionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
  },
  sessionHeaderLeft: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  sessionSport: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginRight: 10,
  },
  statusBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
  },
  statusText: {
    color: '#fff',
    fontSize: 10,
    fontWeight: 'bold',
    textTransform: 'uppercase',
  },
  sessionDate: {
    fontSize: 12,
    color: '#999',
  },
  sessionInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  sessionType: {
    fontSize: 16,
    color: '#333',
    fontWeight: '600',
    marginRight: 10,
  },
  sessionOpponent: {
    fontSize: 14,
    color: '#666',
  },
  matchScoreContainer: {
    marginBottom: 8,
  },
  matchScore: {
    fontSize: 15,
    color: '#007AFF',
    fontWeight: 'bold',
  },
  gameScores: {
    fontSize: 13,
    color: '#666',
    marginTop: 2,
  },
  sessionLocation: {
    fontSize: 14,
    color: '#666',
    marginBottom: 10,
  },
  sessionFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingTop: 10,
    borderTopWidth: 1,
    borderTopColor: '#f0f0f0',
  },
  sessionDuration: {
    fontSize: 14,
    color: '#007AFF',
    fontWeight: '600',
  },
  sessionScoring: {
    fontSize: 12,
    color: '#999',
  },
  emptyState: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 40,
  },
  emptyStateIcon: {
    fontSize: 64,
    marginBottom: 20,
  },
  emptyStateTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 10,
  },
  emptyStateText: {
    fontSize: 14,
    color: '#666',
    textAlign: 'center',
    marginBottom: 30,
  },
  createButton: {
    backgroundColor: '#007AFF',
    borderRadius: 8,
    paddingHorizontal: 24,
    paddingVertical: 12,
  },
  createButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
});
