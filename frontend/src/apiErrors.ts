import i18n from "./i18n";

const EXACT: Record<string, string> = {
  "Corredor no encontrado": "errors.brokerNotFound",
  "Título no encontrado": "errors.instrumentNotFound",
  "Movimiento no encontrado": "errors.tradeNotFound",
  "Objetivo no encontrado": "errors.targetNotFound",
  "Precio no encontrado": "errors.priceNotFound",
  "Ya existe un corredor con ese nombre": "errors.brokerExists",
  "Ya existe un título con ese nombre": "errors.instrumentExists",
  "No se puede inactivar: el título todavía tiene saldo mayor a 0": "errors.cannotInactivate",
  "No se puede comprar un título inactivo; actívelo primero": "errors.cannotBuyInactive",
  "No se puede borrar: hay movimientos con este corredor": "errors.cannotDeleteBroker",
  "No se puede borrar: hay movimientos, precios u objetivos de este título":
    "errors.cannotDeleteInstrument",
  "No se puede borrar: el saldo del corredor quedaría negativo": "errors.cannotDeleteTrade",
  broker_not_found: "errors.brokerNotFound",
  instrument_not_found: "errors.instrumentNotFound",
  trade_not_found: "errors.tradeNotFound",
  target_not_found: "errors.targetNotFound",
  price_not_found: "errors.priceNotFound",
  fx_rate_not_found: "errors.fxNotFound",
  broker_exists: "errors.brokerExists",
  instrument_exists: "errors.instrumentExists",
  cannot_inactivate: "errors.cannotInactivate",
  cannot_buy_inactive: "errors.cannotBuyInactive",
  cannot_delete_broker: "errors.cannotDeleteBroker",
  cannot_delete_instrument: "errors.cannotDeleteInstrument",
  cannot_delete_trade: "errors.cannotDeleteTrade",
  sell_exceeds_balance: "errors.sellExceedsBalance",
};

export function translateApiError(msg: string): string {
  if (EXACT[msg]) return i18n.t(EXACT[msg]);
  if (msg.startsWith("La venta supera el saldo")) return i18n.t("errors.sellExceedsBalance");
  return msg;
}
