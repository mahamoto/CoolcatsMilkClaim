import time
import os
import brownie

sell_price = 2.157

milk_address = "0x1599fE55Cda767b1F631ee7D414b41F5d6dE393d"
treasury_address = "0x11D97F31b489B9c57507839530Ab9EA910979c68"
quickswap_weth_milk_pair = "0xc089c10FB638F36657873137828618aB02bD34aA"

brownie.network.connect("polygon-main")
os.environ["POLYGONSCAN_TOKEN"] = ""

milk = brownie.Contract.from_explorer(milk_address)
treasury = brownie.Contract.from_explorer(treasury_address)
milk_eth_pool = brownie.Contract.from_explorer(quickswap_weth_milk_pair)

base_rate = treasury._baseRate()
cats1_bonus = treasury._catClassBonus(1)
contract_starttime = treasury._contractStartTime()

pool_reserves = milk_eth_pool.getReserves()[:2]
token0 = milk_eth_pool.token0()

def calc_amount_out(amountIn, reserve_in, reserve_out):
    amountIn_with_fee = amountIn * 997
    numerator = amountIn_with_fee * reserve_out
    denominator = reserve_in * 1000 + amountIn_with_fee
    out = numerator // denominator
    assert out < reserve_out, "Calculated output amount is bigger than liquidity!"
    return out

def calc_milk_price(milkIn):
    if token0 == milk_address:
        reserveIn = pool_reserves[0]
        reserveOut = pool_reserves[1]
    else:
        reserveIn = pool_reserves[1]
        reserveOut = pool_reserves[0]
    out = calc_amount_out(milkIn, reserveIn, reserveOut)
    return out

def calc_reward(lastClaim):
    claim_amount = (base_rate+cats1_bonus) * (time.time()-lastClaim) / 86400
    return claim_amount

def calc_claim(catId):
    """
    currently only works for cats1
    """

    lastClaim = treasury._lastUpdate(catId)
    if lastClaim == 0:
        lastClaim = contract_starttime

    claim_amount = calc_reward(lastClaim)

    return claim_amount

if __name__ == "__main__":
    ids = [1,2,3,4]
    max_possible_reward = calc_reward(contract_starttime)
    milk_sum = 0
    for id in ids:
        milk_reward = calc_claim(id)
        milk_sum += milk_reward
        eth_reward = calc_milk_price(milk_reward)
        print(f"Cat with ID: {id} can claim {milk_reward/1e18} MILK -> {eth_reward/1e18} ETH")
    total_eth = calc_milk_price(milk_sum)
    print(f"All cats can claim {milk_sum/1e18} MILK -> {total_eth/1e18} ETH")
    print(f"Max possible claim: {max_possible_reward/1e18} MILK -> {calc_milk_price(max_possible_reward)/1e18} ETH")