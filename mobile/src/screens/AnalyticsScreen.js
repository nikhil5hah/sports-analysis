import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  ActivityIndicator,
  RefreshControl,
} from 'react-native';
import apiClient from '../api/client';

export default function AnalyticsScreen({ navigation }) {
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [sessions, setSessions] = useState([]);
  const [stats, setStats] = useState({
    totalSessions: 0,
    totalMatches: 0,
    totalTraining: 0,
    matchesWon: 0,
    matchesLost: 0,
    totalPoints: 0,
    totalGames: 0,
    averageMatchDuration: 0,
    winRate: 0,
  });

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      const data = await apiClient.getSessions();
      setSessions(data);
      calculateStats(data);
    } catch (error) {
      console.error('Error fetching analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await fetchAnalytics();
    setRefreshing(false);
  };

  const calculateStats = (sessionData) => {
    const completedSessions = sessionData.filter(s => s.end_time);
    const matches = completedSessions.filter(s => s.session_type === 'match');
    const training = completedSessions.filter(s => s.session_type === 'training');

    let matchesWon = 0;
    let matchesLost = 0;
    let totalPoints = 0;
    let totalGames = 0;
    let totalMatchDuration = 0;

    matches.forEach(match => {
      // Count wins/losses
      if (match.final_score_me !== null && match.final_score_opponent !== null) {
        if (match.final_score_me > match.final_score_opponent) {
          matchesWon++;
        } else if (match.final_score_opponent > match.final_score_me) {
          matchesLost++;
        }
      }

      // Sum up points and games
      totalPoints += match.total_points || 0;
      totalGames += match.total_games || 0;

      // Calculate duration
      if (match.end_time && match.start_time) {
        const duration = new Date(match.end_time) - new Date(match.start_time);
        totalMatchDuration += duration;
      }
    });

    const averageMatchDuration = matches.length > 0
      ? Math.floor(totalMatchDuration / matches.length / 1000 / 60) // in minutes
      : 0;

    const winRate = matches.length > 0
      ? Math.round((matchesWon / matches.length) * 100)
      : 0;

    setStats({
      totalSessions: completedSessions.length,
      totalMatches: matches.length,
      totalTraining: training.length,
      matchesWon,
      matchesLost,
      totalPoints,
      totalGames,
      averageMatchDuration,
      winRate,
    });
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#007AFF" />
      </View>
    );
  }

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      <View style={styles.content}>
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.headerTitle}>Performance Analytics</Text>
          <Text style={styles.headerSubtitle}>
            Your squash performance at a glance
          </Text>
        </View>

        {/* Overview Stats */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Overview</Text>
          <View style={styles.statsGrid}>
            <View style={styles.statBox}>
              <Text style={styles.statValue}>{stats.totalSessions}</Text>
              <Text style={styles.statLabel}>Total Sessions</Text>
            </View>
            <View style={styles.statBox}>
              <Text style={styles.statValue}>{stats.totalMatches}</Text>
              <Text style={styles.statLabel}>Matches Played</Text>
            </View>
            <View style={styles.statBox}>
              <Text style={styles.statValue}>{stats.totalTraining}</Text>
              <Text style={styles.statLabel}>Training Sessions</Text>
            </View>
            <View style={styles.statBox}>
              <Text style={styles.statValue}>{stats.averageMatchDuration}m</Text>
              <Text style={styles.statLabel}>Avg Match Time</Text>
            </View>
          </View>
        </View>

        {/* Match Performance */}
        {stats.totalMatches > 0 && (
          <View style={styles.card}>
            <Text style={styles.cardTitle}>Match Performance</Text>

            {/* Win Rate */}
            <View style={styles.winRateContainer}>
              <View style={styles.winRateCircle}>
                <Text style={styles.winRateValue}>{stats.winRate}%</Text>
                <Text style={styles.winRateLabel}>Win Rate</Text>
              </View>
              <View style={styles.winLossStats}>
                <View style={styles.winLossStat}>
                  <View style={[styles.winLossDot, { backgroundColor: '#4CAF50' }]} />
                  <Text style={styles.winLossLabel}>Wins</Text>
                  <Text style={styles.winLossValue}>{stats.matchesWon}</Text>
                </View>
                <View style={styles.winLossStat}>
                  <View style={[styles.winLossDot, { backgroundColor: '#F44336' }]} />
                  <Text style={styles.winLossLabel}>Losses</Text>
                  <Text style={styles.winLossValue}>{stats.matchesLost}</Text>
                </View>
              </View>
            </View>

            {/* Match Stats */}
            <View style={styles.matchStatsRow}>
              <View style={styles.matchStat}>
                <Text style={styles.matchStatValue}>{stats.totalGames}</Text>
                <Text style={styles.matchStatLabel}>Games Played</Text>
              </View>
              <View style={styles.matchStat}>
                <Text style={styles.matchStatValue}>{stats.totalPoints}</Text>
                <Text style={styles.matchStatLabel}>Points Recorded</Text>
              </View>
            </View>
          </View>
        )}

        {/* Biometric Data - Placeholder */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Biometric Data</Text>
          <View style={styles.placeholderContainer}>
            <Text style={styles.placeholderIcon}>⌚</Text>
            <Text style={styles.placeholderTitle}>Coming Soon</Text>
            <Text style={styles.placeholderText}>
              Connect your smartwatch to see heart rate, calories burned,
              distance covered, and more during your matches.
            </Text>
          </View>
        </View>

        {/* Recent Activity */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Recent Activity</Text>
          {sessions.slice(0, 5).map((session, index) => (
            <View key={session.session_id} style={styles.activityItem}>
              <View style={styles.activityIcon}>
                <Text style={styles.activityIconText}>
                  {session.session_type === 'match' ? '🎯' : '💪'}
                </Text>
              </View>
              <View style={styles.activityDetails}>
                <Text style={styles.activityTitle}>
                  {session.session_type === 'match' ? 'Match' : 'Training'}
                  {session.opponent_name && ` vs ${session.opponent_name}`}
                </Text>
                <Text style={styles.activityDate}>
                  {new Date(session.start_time).toLocaleDateString('en-US', {
                    month: 'short',
                    day: 'numeric',
                    year: 'numeric',
                  })}
                </Text>
              </View>
              {session.session_type === 'match' &&
                session.final_score_me !== null &&
                session.final_score_opponent !== null && (
                  <View style={styles.activityScore}>
                    <Text
                      style={[
                        styles.activityScoreText,
                        {
                          color:
                            session.final_score_me > session.final_score_opponent
                              ? '#4CAF50'
                              : '#F44336',
                        },
                      ]}
                    >
                      {session.final_score_me}-{session.final_score_opponent}
                    </Text>
                  </View>
                )}
            </View>
          ))}
          {sessions.length === 0 && (
            <Text style={styles.emptyText}>No sessions yet. Start playing!</Text>
          )}
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
  content: {
    padding: 20,
    paddingBottom: 40,
  },
  header: {
    marginBottom: 24,
  },
  headerTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 8,
  },
  headerSubtitle: {
    fontSize: 16,
    color: '#666',
  },
  card: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 20,
    marginBottom: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  cardTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 16,
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginHorizontal: -8,
  },
  statBox: {
    width: '50%',
    paddingHorizontal: 8,
    paddingVertical: 12,
    alignItems: 'center',
  },
  statValue: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#007AFF',
    marginBottom: 4,
  },
  statLabel: {
    fontSize: 14,
    color: '#666',
    textAlign: 'center',
  },
  winRateContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 20,
  },
  winRateCircle: {
    width: 120,
    height: 120,
    borderRadius: 60,
    backgroundColor: '#f0f7ff',
    borderWidth: 8,
    borderColor: '#007AFF',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 20,
  },
  winRateValue: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#007AFF',
  },
  winRateLabel: {
    fontSize: 14,
    color: '#666',
    marginTop: 4,
  },
  winLossStats: {
    flex: 1,
  },
  winLossStat: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  winLossDot: {
    width: 12,
    height: 12,
    borderRadius: 6,
    marginRight: 8,
  },
  winLossLabel: {
    fontSize: 16,
    color: '#666',
    flex: 1,
  },
  winLossValue: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
  },
  matchStatsRow: {
    flexDirection: 'row',
    borderTopWidth: 1,
    borderTopColor: '#f0f0f0',
    paddingTop: 16,
  },
  matchStat: {
    flex: 1,
    alignItems: 'center',
  },
  matchStatValue: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#007AFF',
    marginBottom: 4,
  },
  matchStatLabel: {
    fontSize: 14,
    color: '#666',
    textAlign: 'center',
  },
  placeholderContainer: {
    alignItems: 'center',
    paddingVertical: 32,
  },
  placeholderIcon: {
    fontSize: 48,
    marginBottom: 16,
  },
  placeholderTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 8,
  },
  placeholderText: {
    fontSize: 14,
    color: '#666',
    textAlign: 'center',
    lineHeight: 20,
    paddingHorizontal: 20,
  },
  activityItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  activityIcon: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#f0f7ff',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  activityIconText: {
    fontSize: 20,
  },
  activityDetails: {
    flex: 1,
  },
  activityTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 4,
  },
  activityDate: {
    fontSize: 14,
    color: '#999',
  },
  activityScore: {
    paddingHorizontal: 12,
    paddingVertical: 4,
    backgroundColor: '#f5f5f5',
    borderRadius: 12,
  },
  activityScoreText: {
    fontSize: 16,
    fontWeight: 'bold',
  },
  emptyText: {
    fontSize: 14,
    color: '#999',
    textAlign: 'center',
    paddingVertical: 20,
  },
});
