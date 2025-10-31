import React, { useState, useEffect } from 'react';
import { View, ActivityIndicator, StyleSheet, TouchableOpacity, Text, Image } from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import apiClient from '../api/client';

// Import custom SVG icons
import SessionsIcon from '../../assets/sessions.svg';
import PlayIcon from '../../assets/play.svg';
import StatsIcon from '../../assets/stats.svg';

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
const Tab = createBottomTabNavigator();

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
      // Auth check error - silently fail
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
      {user ? (
        // Main app with tabs (user is logged in)
        <Tab.Navigator
          initialRouteName="NewSession"
          screenOptions={({ navigation, route }) => ({
            headerStyle: {
              backgroundColor: '#00B89C',
            },
            headerTintColor: '#fff',
            headerTitleStyle: {
              fontWeight: 'bold',
            },
            headerRight: () => (
              <TouchableOpacity
                onPress={handleLogout}
                style={styles.logoutButton}
              >
                <Text style={styles.logoutText}>Logout</Text>
              </TouchableOpacity>
            ),
            tabBarStyle: {
              backgroundColor: '#00B89C',
              borderTopWidth: 0,
              elevation: 0,
              height: 90,
              paddingBottom: 15,
              paddingTop: 15,
            },
            tabBarActiveTintColor: '#fff',
            tabBarInactiveTintColor: 'rgba(255, 255, 255, 0.5)',
            tabBarLabelStyle: {
              fontSize: 13,
              fontWeight: '600',
              marginTop: 5,
            },
            tabBarIconStyle: {
              marginTop: 5,
            },
          })}
        >
          <Tab.Screen
            name="SessionList"
            options={{
              title: 'TRacket',
              tabBarLabel: 'Sessions',
              tabBarIcon: ({ color, size }) => (
                <SessionsIcon width={40} height={40} fill={color} stroke={color} />
              ),
              // Hide tab header, let stack handle it
              headerShown: false,
            }}
          >
            {(props) => (
              <Stack.Navigator
                screenOptions={{
                  headerShown: true,
                  headerStyle: {
                    backgroundColor: '#00B89C',
                  },
                  headerTintColor: '#fff',
                  headerTitleStyle: {
                    fontWeight: 'bold',
                  },
                  headerLeft: () => (
                    <Image
                      source={require('../../assets/logo.png')}
                      style={styles.headerLogo}
                      resizeMode="contain"
                    />
                  ),
                  headerTitle: '',
                  headerRight: () => (
                    <TouchableOpacity
                      onPress={handleLogout}
                      style={styles.logoutButton}
                    >
                      <Text style={styles.logoutText}>Logout</Text>
                    </TouchableOpacity>
                  ),
                }}
              >
                <Stack.Screen
                  name="SessionListMain"
                  component={SessionListScreen}
                  options={{
                    headerTitle: '',
                  }}
                />
                <Stack.Screen
                  name="SessionDetails"
                  component={SessionDetailsScreen}
                  options={{
                    title: 'Session Details',
                  }}
                />
              </Stack.Navigator>
            )}
          </Tab.Screen>

          <Tab.Screen
            name="NewSession"
            options={({ route }) => {
              const routeName = route.state
                ? route.state.routes[route.state.index].name
                : 'SessionCreateMain';

              return {
                title: 'TRacket',
                tabBarLabel: 'Play',
                tabBarIcon: ({ color, size }) => (
                  <PlayIcon width={44} height={44} fill={color} stroke={color} />
                ),
                // Completely hide header for this tab
                headerShown: false,
                // Hide tab bar when on ActiveSession screen
                tabBarStyle: routeName === 'ActiveSession'
                  ? { display: 'none' }
                  : {
                      backgroundColor: '#00B89C',
                      borderTopWidth: 0,
                      elevation: 0,
                      height: 90,
                      paddingBottom: 15,
                      paddingTop: 15,
                    },
              };
            }}
          >
            {(props) => (
              <Stack.Navigator
                screenOptions={{
                  headerShown: true,
                  headerStyle: {
                    backgroundColor: '#00B89C',
                  },
                  headerTintColor: '#fff',
                  headerTitleStyle: {
                    fontWeight: 'bold',
                  },
                  headerLeft: () => (
                    <Image
                      source={require('../../assets/logo.png')}
                      style={styles.headerLogo}
                      resizeMode="contain"
                    />
                  ),
                  headerTitle: '',
                  headerRight: () => (
                    <TouchableOpacity
                      onPress={handleLogout}
                      style={styles.logoutButton}
                    >
                      <Text style={styles.logoutText}>Logout</Text>
                    </TouchableOpacity>
                  ),
                }}
              >
                <Stack.Screen
                  name="SessionCreateMain"
                  component={SessionCreateScreen}
                  options={{
                    headerTitle: '',
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
              </Stack.Navigator>
            )}
          </Tab.Screen>

          <Tab.Screen
            name="Analytics"
            options={{
              title: 'TRacket',
              tabBarLabel: 'Stats',
              tabBarIcon: ({ color, size }) => (
                <StatsIcon width={40} height={40} fill={color} stroke={color} />
              ),
              headerShown: false,
            }}
          >
            {(props) => (
              <Stack.Navigator
                screenOptions={{
                  headerShown: true,
                  headerStyle: {
                    backgroundColor: '#00B89C',
                  },
                  headerTintColor: '#fff',
                  headerTitleStyle: {
                    fontWeight: 'bold',
                  },
                  headerLeft: () => (
                    <Image
                      source={require('../../assets/logo.png')}
                      style={styles.headerLogo}
                      resizeMode="contain"
                    />
                  ),
                  headerTitle: '',
                  headerRight: () => (
                    <TouchableOpacity
                      onPress={handleLogout}
                      style={styles.logoutButton}
                    >
                      <Text style={styles.logoutText}>Logout</Text>
                    </TouchableOpacity>
                  ),
                }}
              >
                <Stack.Screen
                  name="AnalyticsMain"
                  component={AnalyticsScreen}
                  options={{
                    headerTitle: '',
                  }}
                />
              </Stack.Navigator>
            )}
          </Tab.Screen>
        </Tab.Navigator>
      ) : (
        // Auth screens (user is not logged in)
        <Stack.Navigator
          screenOptions={{
            headerStyle: {
              backgroundColor: '#00B89C',
            },
            headerTintColor: '#fff',
            headerTitleStyle: {
              fontWeight: 'bold',
            },
          }}
        >
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
        </Stack.Navigator>
      )}
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
  headerLogo: {
    width: 300,
    height: 90,
    marginLeft: -100,
    tintColor: '#fff',
  },
  logoutButton: {
    marginRight: 15,
    paddingVertical: 6,
    paddingHorizontal: 12,
  },
  logoutText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
});
