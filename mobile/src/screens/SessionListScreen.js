import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  FlatList,
  TouchableOpacity,
  StyleSheet,
  RefreshControl,
  ActivityIndicator,
  Image,
} from 'react-native';
import { useFocusEffect } from '@react-navigation/native';
import apiClient from '../api/client';
import { formatDate, getSessionDuration, formatSportName } from '../utils/formatters';

export default function SessionListScreen({ navigation }) {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const getSportIcon = (sport, sessionType) => {
    if (sessionType === 'training') return { type: 'emoji', value: '💪' };

    switch(sport) {
      case 'tennis':
        return { type: 'emoji', value: '🎾' };
      case 'table_tennis':
        return { type: 'emoji', value: '🏓' };
      case 'badminton':
        return { type: 'emoji', value: '🏸' };
      case 'squash':
        return { type: 'image', value: require('../../assets/squash.jpeg') };
      case 'padel':
        return { type: 'emoji', value: '🎾' }; // Placeholder
      default:
        return { type: 'emoji', value: '🎾' };
    }
  };

  const renderSportIcon = (sport, sessionType) => {
    const icon = getSportIcon(sport, sessionType);
    if (icon.type === 'image') {
      return (
        <Image
          source={icon.value}
          style={styles.sportIcon}
          resizeMode="contain"
        />
      );
    }
    return <Text style={styles.sportEmoji}>{icon.value}</Text>;
  };

  // Reload sessions when screen comes into focus
  useFocusEffect(
    useCallback(() => {
      fetchSessions();
    }, [])
  );

  const fetchSessions = async () => {
    try {
      const data = await apiClient.getSessions();
      setSessions(data);
    } catch (error) {
      // Error fetching sessions - silently fail for now
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    await fetchSessions();
    setRefreshing(false);
  }, []);

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
        if (!item.end_time || item.end_time === null) {
          navigation.navigate('NewSession', {
            screen: 'ActiveSession',
            params: { session: item },
          });
        } else {
          navigation.navigate('SessionDetails', { sessionId: item.session_id });
        }
      }}
    >
      <View style={styles.sessionHeader}>
        <View style={styles.sessionHeaderLeft}>
          <Text style={styles.sessionSport}>{formatSportName(item.sport)}</Text>
        </View>
        <Text style={styles.sessionDate}>{formatDate(item.start_time)}</Text>
      </View>

      <View style={styles.sessionInfo}>
        <View style={styles.sessionTypeContainer}>
          {renderSportIcon(item.sport, item.session_type)}
          <Text style={styles.sessionTypeText}>
            {item.session_type === 'match' ? 'Match' : 'Training'}
          </Text>
        </View>
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

      <View style={styles.sessionFooter}>
        <Text style={styles.sessionDuration}>
          {getSessionDuration(item.start_time, item.end_time)}
        </Text>
        {item.session_type === 'match' && item.scoring_system && (
          <Text style={styles.sessionScoring}>
            {item.scoring_system === 'par_11' ? 'PAR 11' :
             item.scoring_system === 'par_15' ? 'PAR 15' :
             item.scoring_system === 'par_21' ? 'PAR 21' :
             item.scoring_system === 'english' ? 'English' :
             item.scoring_system === 'regular' ? 'Regular' :
             item.scoring_system === 'tiebreak' ? 'Tie-Break' :
             item.scoring_system.toUpperCase()}
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
        onPress={() => navigation.navigate('NewSession')}
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
          onPress={() => navigation.navigate('NewSession', { screen: 'SessionCreateMain' })}
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
    fontSize: 28,
    fontWeight: 'bold',
    color: '#333',
  },
  addButton: {
    backgroundColor: '#00D4AA',
    borderRadius: 8,
    paddingHorizontal: 16,
    paddingVertical: 8,
    shadowColor: '#00D4AA',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.3,
    shadowRadius: 4,
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
  sessionDate: {
    fontSize: 12,
    color: '#999',
  },
  sessionInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  sessionTypeContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  sportEmoji: {
    fontSize: 16,
    marginRight: 6,
  },
  sportIcon: {
    width: 20,
    height: 20,
    marginRight: 6,
  },
  sessionTypeText: {
    fontSize: 16,
    color: '#333',
    fontWeight: '600',
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
    backgroundColor: '#00D4AA',
    borderRadius: 12,
    paddingHorizontal: 24,
    paddingVertical: 14,
    shadowColor: '#00D4AA',
    shadowOffset: { width: 0, height: 3 },
    shadowOpacity: 0.4,
    shadowRadius: 6,
    elevation: 4,
  },
  createButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
    textTransform: 'uppercase',
  },
});
