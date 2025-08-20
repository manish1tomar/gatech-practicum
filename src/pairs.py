import asyncio
import httpx
import ichimoku

BASE_URL = "https://api.crypto.com/exchange/v1"

async def get_usd_pairs():
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{BASE_URL}/public/get-instruments")
        r.raise_for_status()
        data = r.json()
        #print(data["result"]["data"])
        instruments = data["result"]["data"]
        usd_pairs = [
            i["symbol"]
            for i in instruments
            if i["quote_ccy"] == "USD"
        ]
        return usd_pairs

async def get_volume(pair, client, semaphore):
    async with semaphore:
        try:
            r = await client.get(
                f"{BASE_URL}/public/get-tickers",
                params={"instrument_name": pair}
            )
            r.raise_for_status()
            data = r.json()
            #print(data["result"]["data"])
            volume_usd = float(data["result"]["data"][0]["vv"])
            return volume_usd
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                print(f"⚠️ No ticker data for {pair}. Skipping.")
                return None
            else:
                raise
        except Exception as e:
            print(f"⚠️ Error fetching {pair}: {e}")
            return None

async def filter_high_volume_pairs(pairs, min_volume=1_000_000):
    high_volume = []
    semaphore = asyncio.Semaphore(10)  # Limit to 10 concurrent requests
    async with httpx.AsyncClient() as client:
        tasks = []
        for pair in pairs:
            tasks.append(get_volume(pair, client, semaphore))
        volumes = await asyncio.gather(*tasks)
        for pair, vol in zip(pairs, volumes):
            if vol is not None and vol >= min_volume:
                high_volume.append((pair, vol))
    return high_volume

async def main():
    pairs = await get_usd_pairs()
    #pairs = ["XRP_USD"]
    #print(f"Found {len(pairs)} USD pairs. Checking volumes...\n")
    high_volume_pairs = await filter_high_volume_pairs(pairs)
    print("✅ Pairs with 24h USD volume > 1 million:")
    for p, v in high_volume_pairs:
        print(f"{p}: {v:,.2f} USD")
    print([p for p,v in high_volume_pairs])

if __name__ == "__main__":
    asyncio.run(main())
