import React, { useState, useEffect } from 'react';
import { View, ActivityIndicator, StyleSheet } from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import apiClient from '../api/client';

// Import screens
import LoginScreen from '../screens/LoginScreen';
import RegisterScreen from '../screens/RegisterScreen';
import HomeScreen from '../screens/HomeScreen';
import SessionCreateScreen from '../screens/SessionCreateScreen';
import SessionListScreen from '../screens/SessionListScreen';
import ActiveSessionScreen from '../screens/ActiveSessionScreen';
import SessionDetailsScreen from '../screens/SessionDetailsScreen';
import AnalyticsScreen from '../screens/AnalyticsScreen';

const Stack = createNativeStackNavigator();

export default function AppNavigator() {
  const [isLoading, setIsLoading] = useState(true);
  const [user, setUser] = useState(null);

  // Check authentication status on mount
  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      const { isAuthenticated, user: currentUser } = await apiClient.checkAuth();

      if (isAuthenticated) {
        setUser(currentUser);
      }
    } catch (error) {
      console.error('Auth check error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleLoginSuccess = (loggedInUser) => {
    setUser(loggedInUser);
  };

  const handleRegisterSuccess = (registeredUser) => {
    setUser(registeredUser);
  };

  const handleLogout = () => {
    setUser(null);
  };

  // Show loading screen while checking auth
  if (isLoading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#007AFF" />
      </View>
    );
  }

  return (
    <NavigationContainer>
      <Stack.Navigator
        screenOptions={{
          headerStyle: {
            backgroundColor: '#007AFF',
          },
          headerTintColor: '#fff',
          headerTitleStyle: {
            fontWeight: 'bold',
          },
        }}
      >
        {user ? (
          // Main app screens (user is logged in)
          <>
            <Stack.Screen
              name="Home"
              options={{
                title: 'TRacket',
                headerBackVisible: false,
              }}
            >
              {(props) => (
                <HomeScreen
                  {...props}
                  user={user}
                  onLogout={handleLogout}
                />
              )}
            </Stack.Screen>

            <Stack.Screen
              name="SessionCreate"
              component={SessionCreateScreen}
              options={{
                title: 'Create Session',
              }}
            />

            <Stack.Screen
              name="SessionList"
              component={SessionListScreen}
              options={{
                title: 'My Sessions',
              }}
            />

            <Stack.Screen
              name="ActiveSession"
              component={ActiveSessionScreen}
              options={{
                title: 'Active Session',
                headerBackVisible: false,
              }}
            />

            <Stack.Screen
              name="SessionDetails"
              component={SessionDetailsScreen}
              options={{
                title: 'Session Details',
              }}
            />

            <Stack.Screen
              name="Analytics"
              component={AnalyticsScreen}
              options={{
                title: 'Analytics',
              }}
            />
          </>
        ) : (
          // Auth screens (user is not logged in)
          <>
            <Stack.Screen
              name="Login"
              options={{
                title: 'Login',
                headerShown: false,
              }}
            >
              {(props) => (
                <LoginScreen
                  {...props}
                  onLoginSuccess={handleLoginSuccess}
                />
              )}
            </Stack.Screen>

            <Stack.Screen
              name="Register"
              options={{
                title: 'Create Account',
                headerShown: true,
              }}
            >
              {(props) => (
                <RegisterScreen
                  {...props}
                  onRegisterSuccess={handleRegisterSuccess}
                />
              )}
            </Stack.Screen>
          </>
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
}

const styles = StyleSheet.create({
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f5f5f5',
  },
});
