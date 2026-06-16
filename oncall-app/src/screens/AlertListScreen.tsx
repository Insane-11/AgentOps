import { useCallback, useEffect, useState } from "react";
import {
  ActivityIndicator,
  FlatList,
  RefreshControl,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from "react-native";
import { useNavigation, useFocusEffect } from "@react-navigation/native";
import { NativeStackNavigationProp } from "@react-navigation/native-stack";
import { api } from "../api/client";
import { RootStackParamList } from "../../App";

type AlertListNav = NativeStackNavigationProp<RootStackParamList, "AlertList">;

const SEVERITY_COLORS: Record<string, string> = {
  CRITICAL: "#DC2626",
  HIGH: "#EA580C",
  MEDIUM: "#CA8A04",
  LOW: "#16A34A",
};

export default function AlertListScreen() {
  const navigation = useNavigation<AlertListNav>();
  const [incidents, setIncidents] = useState<any[]>([]);
  const [refreshing, setRefreshing] = useState(false);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    try {
      const data = await api.getIncidents();
      setIncidents(
        data.filter((i: any) => i.status !== "RESOLVED")
      );
    } catch {}
  };

  useFocusEffect(
    useCallback(() => {
      load().finally(() => setLoading(false));
    }, [])
  );

  const onRefresh = async () => {
    setRefreshing(true);
    await load();
    setRefreshing(false);
  };

  const renderItem = ({ item }: { item: any }) => (
    <TouchableOpacity
      style={styles.card}
      onPress={() => navigation.navigate("IncidentDetail", { id: item.id })}
    >
      <View style={styles.cardHeader}>
        <View
          style={[
            styles.severityBadge,
            { backgroundColor: SEVERITY_COLORS[item.severity] || "#6B7280" },
          ]}
        >
          <Text style={styles.severityText}>{item.severity}</Text>
        </View>
        <Text style={styles.statusText}>{item.status}</Text>
      </View>
      <Text style={styles.cardTitle}>{item.title}</Text>
      {item.description && (
        <Text style={styles.cardDescription} numberOfLines={2}>
          {item.description}
        </Text>
      )}
      <Text style={styles.cardTime}>
        {new Date(item.created_at).toLocaleString()}
      </Text>
    </TouchableOpacity>
  );

  if (loading) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" color="#4F46E5" />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <FlatList
        data={incidents}
        keyExtractor={(item) => item.id}
        renderItem={renderItem}
        contentContainerStyle={styles.list}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        ListEmptyComponent={
          <Text style={styles.empty}>No active incidents</Text>
        }
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#F3F4F6" },
  centered: { flex: 1, justifyContent: "center", alignItems: "center", backgroundColor: "#F3F4F6" },
  list: { padding: 16 },
  card: {
    backgroundColor: "#fff",
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 2,
  },
  cardHeader: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
    marginBottom: 8,
  },
  severityBadge: {
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 6,
  },
  severityText: { color: "#fff", fontSize: 11, fontWeight: "700" },
  statusText: { fontSize: 12, color: "#6B7280" },
  cardTitle: { fontSize: 16, fontWeight: "600", color: "#111827", marginBottom: 4 },
  cardDescription: { fontSize: 13, color: "#6B7280", marginBottom: 4 },
  cardTime: { fontSize: 11, color: "#9CA3AF" },
  empty: { textAlign: "center", color: "#9CA3AF", marginTop: 48, fontSize: 15 },
});
