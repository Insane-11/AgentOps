import { useCallback, useEffect, useState } from "react";
import {
  ActivityIndicator,
  Alert,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from "react-native";
import { useNavigation, useRoute, RouteProp } from "@react-navigation/native";
import { NativeStackNavigationProp } from "@react-navigation/native-stack";
import { api } from "../api/client";
import { RootStackParamList } from "../../App";

type DetailRoute = RouteProp<RootStackParamList, "IncidentDetail">;
type DetailNav = NativeStackNavigationProp<RootStackParamList, "IncidentDetail">;

const SEVERITY_COLORS: Record<string, string> = {
  CRITICAL: "#DC2626",
  HIGH: "#EA580C",
  MEDIUM: "#CA8A04",
  LOW: "#16A34A",
};

export default function IncidentDetailScreen() {
  const route = useRoute<DetailRoute>();
  const navigation = useNavigation<DetailNav>();
  const [incident, setIncident] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    try {
      const data = await api.getIncident(route.params.id);
      setIncident(data);
    } catch (err: any) {
      Alert.alert("Error", err.message);
      navigation.goBack();
    } finally {
      setLoading(false);
    }
  }, [route.params.id]);

  useEffect(() => {
    load();
  }, [load]);

  const handleAcknowledge = async () => {
    try {
      const updated = await api.acknowledgeIncident(route.params.id);
      setIncident(updated);
      Alert.alert("Acknowledged", "You've taken ownership of this incident.");
    } catch (err: any) {
      Alert.alert("Error", err.message);
    }
  };

  const handleEscalate = async () => {
    Alert.alert("Escalate", "Escalate this incident to CRITICAL?", [
      { text: "Cancel", style: "cancel" },
      {
        text: "Escalate",
        style: "destructive",
        onPress: async () => {
          try {
            const updated = await api.escalateIncident(route.params.id);
            setIncident(updated);
            Alert.alert("Escalated", "Severity raised to CRITICAL.");
          } catch (err: any) {
            Alert.alert("Error", err.message);
          }
        },
      },
    ]);
  };

  const handleResolve = async () => {
    Alert.alert("Resolve", "Mark this incident as resolved?", [
      { text: "Cancel", style: "cancel" },
      {
        text: "Resolve",
        onPress: async () => {
          try {
            await api.resolveIncident(route.params.id);
            navigation.goBack();
          } catch (err: any) {
            Alert.alert("Error", err.message);
          }
        },
      },
    ]);
  };

  if (loading) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" color="#4F46E5" />
      </View>
    );
  }

  if (!incident) return null;

  return (
    <ScrollView style={styles.container}>
      <View style={styles.card}>
        <View style={styles.headerRow}>
          <View
            style={[
              styles.severityBadge,
              { backgroundColor: SEVERITY_COLORS[incident.severity] || "#6B7280" },
            ]}
          >
            <Text style={styles.severityText}>{incident.severity}</Text>
          </View>
          <Text style={styles.statusText}>{incident.status}</Text>
        </View>

        <Text style={styles.title}>{incident.title}</Text>

        {incident.description && (
          <Text style={styles.description}>{incident.description}</Text>
        )}

        <View style={styles.metaRow}>
          <Text style={styles.metaLabel}>Created</Text>
          <Text style={styles.metaValue}>
            {new Date(incident.created_at).toLocaleString()}
          </Text>
        </View>

        {incident.agent_summary && (
          <View style={styles.aiBox}>
            <Text style={styles.aiLabel}>AI Analysis</Text>
            <Text style={styles.aiText}>{incident.agent_summary}</Text>
          </View>
        )}

        <View style={styles.actions}>
          {incident.status === "FIRED" && (
            <TouchableOpacity
              style={[styles.actionBtn, styles.acknowledgeBtn]}
              onPress={handleAcknowledge}
            >
              <Text style={styles.actionBtnText}>Acknowledge</Text>
            </TouchableOpacity>
          )}
          <TouchableOpacity
            style={[styles.actionBtn, styles.escalateBtn]}
            onPress={handleEscalate}
          >
            <Text style={styles.actionBtnText}>Escalate</Text>
          </TouchableOpacity>
          {incident.status !== "RESOLVED" && (
            <TouchableOpacity
              style={[styles.actionBtn, styles.resolveBtn]}
              onPress={handleResolve}
            >
              <Text style={styles.actionBtnText}>Resolve</Text>
            </TouchableOpacity>
          )}
        </View>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#F3F4F6" },
  centered: { flex: 1, justifyContent: "center", alignItems: "center", backgroundColor: "#F3F4F6" },
  card: { backgroundColor: "#fff", margin: 16, borderRadius: 12, padding: 20, shadowColor: "#000", shadowOffset: { width: 0, height: 1 }, shadowOpacity: 0.05, shadowRadius: 4, elevation: 2 },
  headerRow: { flexDirection: "row", alignItems: "center", gap: 8, marginBottom: 12 },
  severityBadge: { paddingHorizontal: 10, paddingVertical: 3, borderRadius: 6 },
  severityText: { color: "#fff", fontSize: 12, fontWeight: "700" },
  statusText: { fontSize: 13, color: "#6B7280" },
  title: { fontSize: 20, fontWeight: "700", color: "#111827", marginBottom: 8 },
  description: { fontSize: 14, color: "#4B5563", lineHeight: 20, marginBottom: 12 },
  metaRow: { flexDirection: "row", justifyContent: "space-between", marginBottom: 12 },
  metaLabel: { fontSize: 12, color: "#9CA3AF" },
  metaValue: { fontSize: 12, color: "#6B7280" },
  aiBox: { backgroundColor: "#EEF2FF", borderRadius: 8, padding: 12, marginBottom: 16 },
  aiLabel: { fontSize: 11, fontWeight: "600", color: "#4F46E5", marginBottom: 4 },
  aiText: { fontSize: 13, color: "#374151", lineHeight: 18 },
  actions: { gap: 10 },
  actionBtn: { borderRadius: 10, padding: 14, alignItems: "center" },
  acknowledgeBtn: { backgroundColor: "#4F46E5" },
  escalateBtn: { backgroundColor: "#DC2626" },
  resolveBtn: { backgroundColor: "#16A34A" },
  actionBtnText: { color: "#fff", fontSize: 15, fontWeight: "600" },
});
