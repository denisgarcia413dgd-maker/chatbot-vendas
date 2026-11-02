import React, { useState } from "react";
import { View, Text, StyleSheet, TextInput, Pressable, ActivityIndicator } from "react-native";
import { useTheme } from "../src/theme";

export default function PainelComandoRobo() {
  const { colors } = useTheme();
  const [url, setUrl] = useState("");
  const [lucro, setLucro] = useState("35"); // 35% de margem desejada por padrão
  const [loading, setLoading] = useState(false);
  const [statusMsg, setStatusMsg] = useState("Aguardando inserção de link tático...");

  const dispararAutomacaoRobo = async () => {
    if (!url) return;
    setLoading(true);
    setStatusMsg("Robô acessando link e analisando custos...");
    
    try {
      // Simulação da chamada de rede para o endpoint do robô criado no backend
      setTimeout(() => {
        setLoading(false);
        setStatusMsg("Sucesso! Produto espelhado e anunciado com margem protetiva.");
        setUrl("");
      }, 2000);
    } catch (err) {
      setLoading(false);
      setStatusMsg("Falha crítica ao executar o scraping do link fornecido.");
    }
  };

  return (
    <View style={[styles.panel, { backgroundColor: colors.surfaceSecondary, borderColor: colors.border }]}>
      <Text style={[styles.panelTitle, { color: colors.onSurface }]}>🤖 CENTRAL DE ARBITRAGEM AUTOMÁTICA</Text>
      <Text style={[styles.description, { color: colors.muted }]}>
        Cole o link direto do produto fornecedor abaixo. O robô cuidará da análise de margem e da conexão do fluxo de pedido.
      </Text>

      <TextInput
        placeholder="Cole o link do produto (Shopee, AliExpress, Partner.Shop...)"
        placeholderTextColor={colors.muted}
        value={url}
        onChangeText={setUrl}
        style={[styles.input, { backgroundColor: colors.surfaceTertiary, color: colors.onSurface, borderColor: colors.border }]}
      />

      <View style={styles.row}>
        <View style={{ flex: 1, marginRight: 8 }}>
          <Text style={[styles.label, { color: colors.onSurfaceTertiary }]}>Margem de Ganho (%)</Text>
          <TextInput
            value={lucro}
            onChangeText={setLucro}
            keyboardType="numeric"
            style={[styles.input, { backgroundColor: colors.surfaceTertiary, color: colors.onSurface, borderColor: colors.border }]}
          />
        </View>
        
        <Pressable 
          onPress={dispararAutomacaoRobo}
          disabled={loading}
          style={({ pressed }) => [
            styles.btnExecutar, 
            { backgroundColor: colors.brandPrimary, opacity: pressed || loading ? 0.7 : 1 }
          ]}
        >
          {loading ? (
            <ActivityIndicator color={colors.onBrandPrimary} size="small" />
          ) : (
            <Text style={[styles.btnText, { color: colors.onBrandPrimary }]}>INICIAR ROBÔ</Text>
          )}
        </Pressable>
      </View>

      <View style={[styles.statusBox, { backgroundColor: colors.surfaceTertiary }]}>
        <Text style={[styles.statusText, { color: colors.info }]}>STATUS: {statusMsg}</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  panel: {
    padding: 16,
    borderRadius: 12,
    borderWidth: 1,
    margin: 16,
  },
  panelTitle: {
    fontSize: 14,
    fontWeight: "700",
    letterSpacing: 0.5,
    marginBottom: 6,
  },
  description: {
    fontSize: 12,
    lineHeight: 16,
    marginBottom: 14,
  },
  input: {
    height: 40,
    borderWidth: 1,
    borderRadius: 6,
    paddingHorizontal: 12,
    fontSize: 13,
    marginBottom: 10,
  },
  row: {
    flexDirection: "row",
    alignItems: "flex-end",
  },
  label: {
    fontSize: 11,
    fontWeight: "600",
    marginBottom: 4,
  },
  btnExecutar: {
    height: 40,
    paddingHorizontal: 20,
    borderRadius: 6,
    justifyContent: "center",
    alignItems: "center",
  },
  btnText: {
    fontSize: 12,
    fontWeight: "700",
  },
  statusBox: {
    marginTop: 12,
    padding: 8,
    borderRadius: 4,
    alignItems: "center",
  },
  statusText: {
    fontSize: 11,
    fontWeight: "600",
    fontFamily: "Rajdhani",
  },
});
