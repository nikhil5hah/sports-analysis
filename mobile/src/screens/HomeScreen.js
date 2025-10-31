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
import { COLORS } from '../constants/colors';

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
      {/* Logout Button - Top Right */}
      <TouchableOpacity
        style={styles.logoutButtonTop}
        onPress={handleLogout}
      >
        <Text style={styles.logoutIconTop}>⏻</Text>
      </TouchableOpacity>

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

      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.background,
  },
  logoutButtonTop: {
    position: 'absolute',
    top: 50,
    right: 20,
    zIndex: 10,
    width: 50,
    height: 50,
    borderRadius: 25,
    backgroundColor: COLORS.error,
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: COLORS.shadow,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
    elevation: 5,
  },
  logoutIconTop: {
    fontSize: 28,
    color: COLORS.textWhite,
    fontWeight: 'bold',
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
  welcomeText: {
    fontSize: 20,
    color: COLORS.textPrimary,
    fontWeight: '600',
    marginBottom: 8,
  },
  emailText: {
    fontSize: 14,
    color: COLORS.textSecondary,
  },
  actionsContainer: {
    marginBottom: 24,
  },
  actionCard: {
    borderRadius: 12,
    padding: 24,
    marginBottom: 15,
    alignItems: 'center',
    shadowColor: COLORS.shadow,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  primaryCard: {
    backgroundColor: COLORS.buttonSecondary,
  },
  secondaryCard: {
    backgroundColor: COLORS.cardBackground,
    borderWidth: 2,
    borderColor: COLORS.buttonSecondary,
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
});
