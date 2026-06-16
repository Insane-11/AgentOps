import { NavigationContainer } from "@react-navigation/native";
import { createNativeStackNavigator } from "@react-navigation/native-stack";
import { StatusBar } from "expo-status-bar";
import { useEffect, useState } from "react";
import { ActivityIndicator, View } from "react-native";

import LoginScreen from "./src/screens/LoginScreen";
import AlertListScreen from "./src/screens/AlertListScreen";
import IncidentDetailScreen from "./src/screens/IncidentDetailScreen";
import { api } from "./src/api/client";
import * as Notifications from "expo-notifications";

export type RootStackParamList = {
  Login: undefined;
  AlertList: undefined;
  IncidentDetail: { id: string };
};

const Stack = createNativeStackNavigator<RootStackParamList>();

Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: true,
  }),
});

export default function App() {
  const [loading, setLoading] = useState(true);
  const [authenticated, setAuthenticated] = useState(false);

  useEffect(() => {
    const token = api.loadToken();
    if (token) {
      setAuthenticated(true);
    }
    setLoading(false);
  }, []);

  if (loading) {
    return (
      <View style={{ flex: 1, justifyContent: "center", alignItems: "center", backgroundColor: "#F9FAFB" }}>
        <ActivityIndicator size="large" color="#4F46E5" />
      </View>
    );
  }

  return (
    <NavigationContainer>
      <StatusBar style="dark" />
      <Stack.Navigator
        screenOptions={{
          headerStyle: { backgroundColor: "#4F46E5" },
          headerTintColor: "#fff",
          headerTitleStyle: { fontWeight: "600" },
        }}
      >
        {authenticated ? (
          <>
            <Stack.Screen
              name="AlertList"
              component={AlertListScreen}
              options={{ title: "AgentOps On-Call" }}
            />
            <Stack.Screen
              name="IncidentDetail"
              component={IncidentDetailScreen}
              options={{ title: "Incident" }}
            />
          </>
        ) : (
          <Stack.Screen
            name="Login"
            component={LoginScreen}
            options={{ title: "AgentOps Login" }}
          />
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
}
