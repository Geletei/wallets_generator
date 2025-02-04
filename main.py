import pandas as pd
from eth_account import Account
from bip_utils import Bip39MnemonicGenerator, Bip32Slip10Ed25519, Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes
import hashlib
from solders.keypair import Keypair
from web3 import Web3
import bech32

mnemon_num = 12


def generate_solana_wallets(count):
    generated_wallets = []

    for _ in range(count):
        mnemonic_generator = Bip39MnemonicGenerator()
        mnemonic = mnemonic_generator.FromWordsNumber(words_num=mnemon_num)

        seed_bytes = Bip39SeedGenerator(mnemonic).Generate("")
        bip44_mst_ctx = Bip44.FromSeed(seed_bytes, Bip44Coins.SOLANA)
        bip44_acc_ctx = bip44_mst_ctx.Purpose().Coin().Account(0)
        bip44_chg_ctx = bip44_acc_ctx.Change(Bip44Changes.CHAIN_EXT)

        keypair = Keypair.from_seed(bip44_chg_ctx.PrivateKey().Raw().ToBytes())

        generated_wallets.append({
            'address': keypair.pubkey(),
            'private_key': keypair,
            'mnemonic': mnemonic,
        })

    return generated_wallets


def generate_sui_wallets(count):
    generated_wallets = []

    for _ in range(count):
        SUI_DEFAULT_DERIVATION_PATH = "m/44'/784'/0'/0'/0'"
        mnemonic_generator = Bip39MnemonicGenerator()
        mnemonic = mnemonic_generator.FromWordsNumber(words_num=mnemon_num)

        bip39_seed = Bip39SeedGenerator(mnemonic).Generate()
        bip32_ctx = Bip32Slip10Ed25519.FromSeed(bip39_seed)
        bip32_der_ctx = bip32_ctx.DerivePath(SUI_DEFAULT_DERIVATION_PATH)

        bip44_ctx = Bip44.FromSeed(bip39_seed, Bip44Coins.SUI)
        private_key = bip44_ctx.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(
            0).PrivateKey().Raw().ToBytes()
        private_key_33 = b"\x00" + private_key
        bech32_encoded_key = bech32.bech32_encode("suiprivkey", bech32.convertbits(private_key_33, 8, 5))
        address = "0x" + hashlib.blake2b(
            bip32_der_ctx.PublicKey().RawCompressed().ToBytes(),
            digest_size=32).hexdigest()[:64]

        generated_wallets.append({
            'address': address,
            'private_key': bech32_encoded_key,
            'mnemonic': mnemonic,
        })

    return generated_wallets


def generate_ethereum_wallets(count):
    generated_wallets = []

    for _ in range(count):
        mnemonic_generator = Bip39MnemonicGenerator()
        mnemonic = mnemonic_generator.FromWordsNumber(words_num=mnemon_num)
        seed = Bip39SeedGenerator(mnemonic).Generate()
        bip_obj = Bip44.FromSeed(seed, Bip44Coins.ETHEREUM)
        private_key = bip_obj.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(0).PrivateKey().Raw().ToBytes()
        account = Account.from_key(private_key)

        generated_wallets.append({
            'address': Web3.to_checksum_address(account.address),
            'private_key': '0x' + str(private_key.hex()),
            'mnemonic': mnemonic,
        })

    return generated_wallets


def save_wallets_to_csv(wallets, file_name):
    df = pd.DataFrame(wallets, columns=['address', 'private_key', 'mnemonic'])
    df.columns = ['Wallets', 'Private Key', 'Seed Phrases']
    df.to_csv(file_name, index=False)


if __name__ == '__main__':
    wallet_type = int(input("Які гаманці генерувати:\n1. EVM\n2. Solana\n3. Sui\n>>> "))
    if wallet_type in [1, 2, 3]:
        count = int(input("Кількість гаманців для генерації: "))
        if wallet_type == 1:
            wallets = generate_ethereum_wallets(count)
        elif wallet_type == 2:
            wallets = generate_solana_wallets(count)
        elif wallet_type == 3:
            wallets = generate_sui_wallets(count)
        save_wallets_to_csv(wallets, 'wallets.csv')
        print(f"\nЗгенеровано {count} гаманців і збережено в файлі wallets.csv")
    else:
        print("Невірно обрано варіант.")
