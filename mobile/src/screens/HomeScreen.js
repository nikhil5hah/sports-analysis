import React from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  SafeAreaView,
  Alert,
  Platform,
  Image,
} from 'react-native';
import apiClient from '../api/client';

export default function HomeScreen({ user, onLogout, navigation }) {
  const handleLogout = async () => {
    if (Platform.OS === 'web') {
      const confirmed = window.confirm('Are you sure you want to logout?');
      if (confirmed) {
        await apiClient.logout();
        if (onLogout) {
          onLogout();
        }
      }
    } else {
      Alert.alert(
        'Logout',
        'Are you sure you want to logout?',
        [
          {
            text: 'Cancel',
            style: 'cancel',
          },
          {
            text: 'Logout',
            onPress: async () => {
              await apiClient.logout();
              if (onLogout) {
                onLogout();
              }
            },
            style: 'destructive',
          },
        ]
      );
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.content}>
        {/* Header */}
        <View style={styles.header}>
          <Image
            source={require('../../assets/logo.png')}
            style={styles.logo}
            resizeMode="contain"
          />
          <Text style={styles.welcomeText}>
            Welcome, {user?.name || 'User'}!
          </Text>
          <Text style={styles.emailText}>{user?.email}</Text>
        </View>

        {/* Main Actions */}
        <View style={styles.actionsContainer}>
          <TouchableOpacity
            style={[styles.actionCard, styles.primaryCard]}
            onPress={() => navigation.navigate('SessionCreate')}
          >
            <Text style={styles.actionIcon}>➕</Text>
            <Text style={[styles.actionTitle, { color: '#fff' }]}>New Session</Text>
            <Text style={[styles.actionDescription, { color: '#fff' }]}>
              Start tracking a match or training
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.actionCard, styles.secondaryCard]}
            onPress={() => navigation.navigate('SessionList')}
          >
            <Text style={styles.actionIcon}>📊</Text>
            <Text style={[styles.actionTitle, { color: '#007AFF' }]}>My Sessions</Text>
            <Text style={[styles.actionDescription, { color: '#007AFF', opacity: 1 }]}>
              View your session history
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.actionCard, styles.secondaryCard]}
            onPress={() => navigation.navigate('Analytics')}
          >
            <Text style={styles.actionIcon}>📈</Text>
            <Text style={[styles.actionTitle, { color: '#007AFF' }]}>Analytics</Text>
            <Text style={[styles.actionDescription, { color: '#007AFF', opacity: 1 }]}>
              View your performance stats
            </Text>
          </TouchableOpacity>
        </View>

        {/* Info Box */}
        <View style={styles.infoBox}>
          <Text style={styles.infoTitle}>✨ Phase 4 & 5 Complete!</Text>
          <Text style={styles.infoText}>
            Score tracking and analytics are ready! Track points in real-time and analyze your performance with comprehensive stats.
          </Text>
        </View>

        {/* Coming Soon */}
        <View style={styles.comingSoonBox}>
          <Text style={styles.comingSoonTitle}>Coming Next (Phase 3):</Text>
          <Text style={styles.comingSoonItem}>• Pixel Watch 3 integration</Text>
          <Text style={styles.comingSoonItem}>• Real-time heart rate tracking</Text>
          <Text style={styles.comingSoonItem}>• Biometric data visualization</Text>
          <Text style={styles.comingSoonItem}>• Player Mode (watch-controlled scoring)</Text>
        </View>

        {/* Logout Button */}
        <TouchableOpacity
          style={styles.logoutButton}
          onPress={handleLogout}
        >
          <Text style={styles.logoutButtonText}>Logout</Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  content: {
    flex: 1,
    padding: 20,
    justifyContent: 'center',
  },
  header: {
    alignItems: 'center',
    marginBottom: 40,
  },
  logo: {
    width: 200,
    height: 80,
    marginBottom: 20,
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 20,
  },
  welcomeText: {
    fontSize: 20,
    color: '#333',
    fontWeight: '600',
    marginBottom: 8,
  },
  emailText: {
    fontSize: 14,
    color: '#666',
  },
  actionsContainer: {
    marginBottom: 24,
  },
  actionCard: {
    borderRadius: 12,
    padding: 24,
    marginBottom: 15,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  primaryCard: {
    backgroundColor: '#007AFF',
  },
  secondaryCard: {
    backgroundColor: '#fff',
    borderWidth: 2,
    borderColor: '#007AFF',
  },
  actionIcon: {
    fontSize: 48,
    marginBottom: 12,
  },
  actionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 8,
    color: '#fff',
  },
  actionDescription: {
    fontSize: 14,
    textAlign: 'center',
    color: '#fff',
    opacity: 0.9,
  },
  infoBox: {
    backgroundColor: '#d4edda',
    borderRadius: 12,
    padding: 16,
    marginBottom: 20,
    borderWidth: 1,
    borderColor: '#c3e6cb',
  },
  infoTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#155724',
    marginBottom: 6,
  },
  infoText: {
    fontSize: 14,
    color: '#155724',
  },
  comingSoonBox: {
    backgroundColor: '#fff3cd',
    borderRadius: 12,
    padding: 16,
    marginBottom: 24,
    borderWidth: 1,
    borderColor: '#ffc107',
  },
  comingSoonTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#856404',
    marginBottom: 8,
  },
  comingSoonItem: {
    fontSize: 12,
    color: '#856404',
    marginBottom: 4,
    marginLeft: 8,
  },
  logoutButton: {
    backgroundColor: '#dc3545',
    borderRadius: 8,
    padding: 15,
    alignItems: 'center',
  },
  logoutButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
});
