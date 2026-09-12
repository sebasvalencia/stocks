import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";
import { api, type PendingPrices } from "./api";

export function currentMonth(): { year: number; month: number } {
  const today = new Date();
  return { year: today.getFullYear(), month: today.getMonth() + 1 };
}

type Props = {
  linkToPrices?: boolean;
  reload?: number;
};

export default function BannerPrecios({ linkToPrices = false, reload = 0 }: Props) {
  const { t } = useTranslation();
  const { year, month } = currentMonth();
  const [data, setData] = useState<PendingPrices | null>(null);

  useEffect(() => {
    api.pendingPrices(year, month).then(setData).catch(() => setData(null));
  }, [year, month, reload]);

  if (!data || data.pending === 0) return null;

  const names = data.missing.map((f) => f.instrument_name).join(", ");
  const monthName = t(`months.long.${month - 1}`);
  const text =
    data.pending === 1
      ? t("banner.one", { month: monthName, total: data.total_active })
      : t("banner.many", { count: data.pending, month: monthName, total: data.total_active });

  return (
    <p className="rounded border border-amber-300 bg-amber-50 px-3 py-2 text-sm text-amber-950">
      {text} {names}.
      {linkToPrices && (
        <>
          {" "}
          <Link to="/prices" className="underline">
            {t("banner.load")}
          </Link>
        </>
      )}
    </p>
  );
}
