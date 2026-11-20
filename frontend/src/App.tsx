import React from "react";
import { View, Text, TouchableOpacity, ScrollView, StyleSheet } from "react-native";
import { BotProvider, useBot } from "./bot";

function Tela() {
  const { active, running, logs, stats, toggle, clearLogs } = useBot();
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Robô de Vendas</Text>
      <Text style={styles.status}>{active ? "🟢 LIGADO" : "🔴 DESLIGADO"} {running ? "- verificando..." : ""}</Text>

      <TouchableOpacity style={[styles.btn, { backgroundColor: active ? "#e74c3c" : "#27ae60" }]} onPress={toggle}>
        <Text style={styles.btnText}>{active ? "DESLIGAR" : "LIGAR ROBÔ"}</Text>
      </TouchableOpacity>

      <TouchableOpacity style={styles.btn2} onPress={clearLogs}>
        <Text style={styles.btnText}>Limpar Logs</Text>
      </TouchableOpacity>

      {stats && <Text style={styles.stats}>Vendas: {stats.total_vendas} | Lucro: R$ {stats.lucro_total}</Text>}

      <ScrollView style={styles.logs}>
        {logs.map((l, i) => (
          <Text key={i} style={styles.log}>• {l.message}</Text>
        ))}
      </ScrollView>
    </View>
  );
}

export default function App() {
  return <BotProvider><Tela /></BotProvider>;
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 20, paddingTop: 60, backgroundColor: "#fff" },
  title: { fontSize: 26, fontWeight: "bold", textAlign: "center" },
  status: { fontSize: 18, textAlign: "center", marginVertical: 15 },
  btn: { padding: 16, borderRadius: 10, alignItems: "center", marginVertical: 5 },
  btn2: { padding: 12, borderRadius: 10, alignItems: "center", backgroundColor: "#333", marginVertical: 5 },
  btnText: { color: "#fff", fontWeight: "bold", fontSize: 16 },
  stats: { textAlign: "center", marginVertical: 10, fontSize: 16 },
  logs: { marginTop: 10 },
  log: { fontSize: 14, marginVertical: 3 },
});
