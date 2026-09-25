import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";
import { api, type PendingPrices, type PendingUnitValues } from "./api";

export function currentMonth(): { year: number; month: number } {
  const today = new Date();
  return { year: today.getFullYear(), month: today.getMonth() + 1 };
}

type Kind = "equities" | "funds" | "both";

type Props = {
  linkToPrices?: boolean;
  reload?: number;
  kind?: Kind;
};

export default function BannerPrecios({ linkToPrices = false, reload = 0, kind = "equities" }: Props) {
  const { t } = useTranslation();
  const { year, month } = currentMonth();
  const [equities, setEquities] = useState<PendingPrices | null>(null);
  const [funds, setFunds] = useState<PendingUnitValues | null>(null);

  useEffect(() => {
    if (kind === "equities" || kind === "both") {
      api.pendingPrices(year, month).then(setEquities).catch(() => setEquities(null));
    }
    if (kind === "funds" || kind === "both") {
      api.pendingFundUnitValues(year, month).then(setFunds).catch(() => setFunds(null));
    }
  }, [year, month, reload, kind]);

  const monthName = t(`months.long.${month - 1}`);
  const showEq = (kind === "equities" || kind === "both") && equities != null && equities.pending > 0;
  const showFd = (kind === "funds" || kind === "both") && funds != null && funds.pending > 0;
  if (!showEq && !showFd) return null;

  return (
    <div className="space-y-2">
      {showEq && equities && (
        <p className="rounded border border-warn/40 bg-warn/10 px-3 py-2 text-sm text-warn">
          {equities.pending === 1
            ? t("banner.one", { month: monthName, total: equities.total_active })
            : t("banner.many", { count: equities.pending, month: monthName, total: equities.total_active })}{" "}
          {equities.missing.map((f) => f.instrument_name).join(", ")}.
          {linkToPrices && (
            <>
              {" "}
              <Link to="/prices" className="underline">
                {t("banner.load")}
              </Link>
            </>
          )}
        </p>
      )}
      {showFd && funds && (
        <p className="rounded border border-warn/40 bg-warn/10 px-3 py-2 text-sm text-warn">
          {funds.pending === 1
            ? t("banner.fundsOne", { month: monthName, total: funds.total_active })
            : t("banner.fundsMany", { count: funds.pending, month: monthName, total: funds.total_active })}{" "}
          {funds.missing.map((f) => f.fund_name).join(", ")}.
          {linkToPrices && (
            <>
              {" "}
              <Link to="/funds/prices" className="underline">
                {t("banner.fundsLoad")}
              </Link>
            </>
          )}
        </p>
      )}
    </div>
  );
}
