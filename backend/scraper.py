import logging
import warnings

import requests
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

logger = logging.getLogger(__name__)

def fetch_odds(race_id: str, combinations: set[str] | None = None) -> list[dict]:
    """boatrace.jp から三連単オッズを取得する。

    Args:
        race_id: "YYYYMMDDJJRR" 形式 (8桁=開催日, 2桁=場コード, 2桁=レース番号)
        combinations: 取得する買い目のセット。None なら全買い目を返す。

    Returns:
        [{"combination": "2-3-5", "odds": 45.0}, ...]
    """
    hd = race_id[:8]
    jcd = race_id[8:10]
    rno = str(int(race_id[10:12]))

    url = (
        f"https://www.boatrace.jp/owpc/pc/race/odds3t"
        f"?rno={rno}&jcd={jcd}&hd={hd}"
    )

    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as e:
        logger.error("オッズページの取得に失敗: %s", e)
        return []

    soup = BeautifulSoup(resp.content, "lxml")
    tbody = soup.select_one("tbody.is-p3-0")
    if tbody is None:
        logger.error("オッズテーブルが見つかりません (race_id=%s)", race_id)
        return []

    results = []
    second_place = [0] * 6  # 各列(1着艇)の現在の2着艇番を保持

    for row in tbody.find_all("tr"):
        cells = row.find_all("td")
        col = 0  # 列インデックス (0=1着が1号艇, ..., 5=1着が6号艇)
        i = 0

        while i < len(cells) and col < 6:
            cell = cells[i]

            # rowspan 付きセル = 2着の艇番
            if cell.get("rowspan"):
                try:
                    second_place[col] = int(cell.get_text(strip=True))
                except ValueError:
                    col += 1
                    i += 1
                    continue
                i += 1

            # 3着の艇番
            try:
                third = int(cells[i].get_text(strip=True))
            except (ValueError, IndexError):
                col += 1
                i += 1
                continue
            i += 1

            # オッズ値
            try:
                odds_text = cells[i].get_text(strip=True)
            except IndexError:
                col += 1
                continue
            i += 1

            first = col + 1
            combo = f"{first}-{second_place[col]}-{third}"

            if combinations is None or combo in combinations:
                try:
                    odds = float(odds_text)
                    results.append({"combination": combo, "odds": odds})
                except ValueError:
                    logger.warning("オッズのパースに失敗: %s = '%s'", combo, odds_text)

            col += 1

    return results


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    race_id = "202504130412"
    print(f"race_id: {race_id}")
    data = fetch_odds(race_id)
    if data:
        for item in data:
            print(f"  {item['combination']}: {item['odds']}")
    else:
        print("  取得できませんでした")
