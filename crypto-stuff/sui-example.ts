import axios from 'axios';

// Example usage of the SUI Testnet API

const API_BASE_URL = 'http://localhost:3000';

// Your keypair from the error message
const YOUR_WALLET = {
    suiAddress: "0xbf8ba70997c705101fa3bbd478a6c87e884a34196408a08c40d90f0b5ae59511",
    publicKey: "aa9c3925c86d265e3dc3b4ad6bf869620fb180be807e4cc8c72dc7acf720725f",
    privateKey: "suiprivkey1qzp4fnv6nhwq0nn758mz62vej8a4gzq92ne7yy7lmekter550us2qhp8nav"
};

async function runExample() {
    console.log("SUI Testnet Transaction Example");
    console.log("================================\n");

    try {
        // Step 1: Check current balance
        console.log("Step 1: Checking balance of your wallet...");
        const balanceResponse = await axios.get(`${API_BASE_URL}/balance/${YOUR_WALLET.suiAddress}`);
        console.log("Current balance:", balanceResponse.data.balanceInSUI, "SUI");
        console.log("Coin count:", balanceResponse.data.coinObjectCount);

        // Step 2: If balance is 0, request from faucet
        if (parseInt(balanceResponse.data.totalBalance) === 0) {
            console.log("\nStep 2: Balance is 0, requesting SUI from faucet...");
            const faucetResponse = await axios.post(`${API_BASE_URL}/faucet`, {
                address: YOUR_WALLET.suiAddress
            });

            if (faucetResponse.data.success) {
                console.log("✅ Faucet request successful!");
                console.log("Waiting 10 seconds for transaction to be processed...");
                await new Promise(resolve => setTimeout(resolve, 10000));

                // Check balance again
                const newBalanceResponse = await axios.get(`${API_BASE_URL}/balance/${YOUR_WALLET.suiAddress}`);
                console.log("New balance:", newBalanceResponse.data.balanceInSUI, "SUI");
            } else {
                console.log("❌ Faucet request failed:", faucetResponse.data.message);
                console.log("You might be rate limited. Try again later or use the official faucet:");
                console.log("https://discord.com/channels/916379725201563759/1037811694564560966");
                return;
            }
        }

        // Step 3: Send a small amount of SUI
        console.log("\nStep 3: Sending 0.001 SUI to a test address...");
        const recipientAddress = "0x5d90e6a9c2d7ccaa1dc3a99a6e780ebcc199bb999b26134195a328cb5df151cb";

        const sendResponse = await axios.post(`${API_BASE_URL}/send-sui`, {
            privateKey: YOUR_WALLET.privateKey,
            recipientAddress: recipientAddress,
            amount: 1000000  // 0.001 SUI
        });

        if (sendResponse.data.success) {
            console.log("✅ Transaction successful!");
            console.log("Transaction digest:", sendResponse.data.transactionDigest);
            console.log("Explorer URL:", sendResponse.data.explorerUrl);
            console.log("Amount sent:", sendResponse.data.amountInSUI, "SUI");
            console.log("Verified:", sendResponse.data.verified);

            // Step 4: Verify the transaction
            console.log("\nStep 4: Verifying transaction on chain...");
            const verifyResponse = await axios.get(`${API_BASE_URL}/verify/${sendResponse.data.transactionDigest}`);
            console.log("Transaction verification:", verifyResponse.data.success ? "✅ Confirmed" : "❌ Failed");

            if (verifyResponse.data.gasUsed) {
                console.log("Gas used:", JSON.stringify(verifyResponse.data.gasUsed));
            }
        } else {
            console.log("❌ Transaction failed:", sendResponse.data.message);

            if (sendResponse.data.needsFaucet) {
                console.log("\n💡 Tip:", sendResponse.data.faucetMessage);
            }
        }

        // Step 5: Check final balance
        console.log("\nStep 5: Checking final balance...");
        const finalBalanceResponse = await axios.get(`${API_BASE_URL}/balance/${YOUR_WALLET.suiAddress}`);
        console.log("Final balance:", finalBalanceResponse.data.balanceInSUI, "SUI");

    } catch (error: any) {
        console.error("\n❌ Error:", error.response?.data || error.message);

        if (error.code === 'ECONNREFUSED') {
            console.log("\n💡 Make sure the server is running:");
            console.log("   npm run dev");
            console.log("   or");
            console.log("   npx ts-node suicrypto.ts");
        }
    }
}

// Alternative: Generate a new keypair
async function generateNewKeypair() {
    console.log("\nGenerating new keypair...");
    try {
        const response = await axios.get(`${API_BASE_URL}/generate-keypair`);
        console.log("\n✨ New Keypair Generated:");
        console.log("Address:", response.data.keypair.suiAddress);
        console.log("Private Key:", response.data.keypair.privateKey);
        console.log("Public Key:", response.data.keypair.publicKey);
        console.log("\nBalance:", response.data.balance.balanceInSUI, "SUI");
        console.log("Explorer:", response.data.explorerUrl);
        console.log("\n💡 Save your private key securely! You'll need it to access your wallet.");

        return response.data.keypair;
    } catch (error: any) {
        console.error("Failed to generate keypair:", error.response?.data || error.message);
    }
}

// Run the example
console.log("Starting SUI Testnet Example...\n");
console.log("This example will:");
console.log("1. Check your wallet balance");
console.log("2. Request test SUI from faucet if needed");
console.log("3. Send a small transaction");
console.log("4. Verify the transaction");
console.log("5. Check final balance\n");

runExample().then(() => {
    console.log("\n✅ Example completed!");
}).catch(console.error);

// Uncomment to generate a new keypair instead
// generateNewKeypair();