import axios from 'axios';

// Script to send SUI from the funded wallet (2 SUI balance)

const API_BASE_URL = 'http://localhost:3000';

// Wallet with 2 SUI (sender) - CORRECT PRIVATE KEY
const FUNDED_WALLET = {
    address: "0x5d90e6a9c2d7ccaa1dc3a99a6e780ebcc199bb999b26134195a328cb5df151cb",
    privateKey: "suiprivkey1qrdkvfpf9ksrsh8pwayg6n8vgk5n89087fy05u9uavvwsd6egv5ezxt843t",
    currentBalance: "~1.99 SUI"
};

// Your other wallet (recipient) - the one without funds
const RECIPIENT_WALLET = {
    address: "0xbf8ba70997c705101fa3bbd478a6c87e884a34196408a08c40d90f0b5ae59511"
};

async function sendFromFundedWallet() {
    console.log("======================================");
    console.log("SUI Transfer from Funded Wallet");
    console.log("======================================\n");

    try {
        // Step 1: Check balance of sender wallet
        console.log("Step 1: Checking balance of sender wallet...");
        console.log("Sender Address:", FUNDED_WALLET.address);

        const senderBalance = await axios.get(`${API_BASE_URL}/balance/${FUNDED_WALLET.address}`);
        console.log("Current balance:", senderBalance.data.balanceInSUI, "SUI");
        console.log("Coin count:", senderBalance.data.coinObjectCount);
        console.log("Total balance in MIST:", senderBalance.data.totalBalance);

        if (parseInt(senderBalance.data.totalBalance) === 0) {
            console.log("❌ This wallet has no SUI. Cannot send.");
            return;
        }

        // Step 2: Check balance of recipient wallet
        console.log("\nStep 2: Checking balance of recipient wallet...");
        console.log("Recipient Address:", RECIPIENT_WALLET.address);

        const recipientBalance = await axios.get(`${API_BASE_URL}/balance/${RECIPIENT_WALLET.address}`);
        console.log("Recipient balance:", recipientBalance.data.balanceInSUI, "SUI");

        // Step 3: Send SUI
        console.log("\n======================================");
        console.log("Step 3: Sending 0.0001 SUI...");
        console.log("======================================");

        const amountToSend = 100000; // 0.0001 SUI (100,000 MIST)
        console.log("Amount to send: 0.0001 SUI (", amountToSend, "MIST)");
        console.log("From:", FUNDED_WALLET.address);
        console.log("To:", RECIPIENT_WALLET.address);
        console.log("\nInitiating transaction...");

        const sendResponse = await axios.post(`${API_BASE_URL}/send-sui`, {
            privateKey: FUNDED_WALLET.privateKey,
            recipientAddress: RECIPIENT_WALLET.address,
            amount: amountToSend
        });

        if (sendResponse.data.success) {
            console.log("\n✅ TRANSACTION SUCCESSFUL!");
            console.log("======================================");
            console.log("Transaction Details:");
            console.log("- Digest:", sendResponse.data.transactionDigest);
            console.log("- Amount sent:", sendResponse.data.amountInSUI, "SUI");
            console.log("- From:", sendResponse.data.senderAddress);
            console.log("- To:", sendResponse.data.recipientAddress);
            console.log("- Verified:", sendResponse.data.verified ? "✓" : "✗");
            console.log("- Explorer URL:", sendResponse.data.explorerUrl);

            // Step 4: Verify transaction
            console.log("\nStep 4: Verifying transaction on chain...");
            const verifyResponse = await axios.get(`${API_BASE_URL}/verify/${sendResponse.data.transactionDigest}`);

            if (verifyResponse.data.success) {
                console.log("✅ Transaction confirmed on blockchain!");
                if (verifyResponse.data.gasUsed) {
                    const gasAmount = verifyResponse.data.gasUsed.computationCost;
                    const storageCost = verifyResponse.data.gasUsed.storageCost;
                    const storageRebate = verifyResponse.data.gasUsed.storageRebate;
                    console.log("Gas details:");
                    console.log("- Computation cost:", gasAmount);
                    console.log("- Storage cost:", storageCost);
                    console.log("- Storage rebate:", storageRebate);
                }
            }

            // Step 5: Check final balances
            console.log("\n======================================");
            console.log("Step 5: Checking final balances...");
            console.log("======================================");

            // Wait a moment for balances to update
            await new Promise(resolve => setTimeout(resolve, 2000));

            const finalSenderBalance = await axios.get(`${API_BASE_URL}/balance/${FUNDED_WALLET.address}`);
            const finalRecipientBalance = await axios.get(`${API_BASE_URL}/balance/${RECIPIENT_WALLET.address}`);

            console.log("\nFinal Balances:");
            console.log("Sender:", finalSenderBalance.data.balanceInSUI, "SUI (was", senderBalance.data.balanceInSUI, "SUI)");
            console.log("Recipient:", finalRecipientBalance.data.balanceInSUI, "SUI (was", recipientBalance.data.balanceInSUI, "SUI)");

            console.log("\n✅ Transfer completed successfully!");
            console.log("Your wallet", RECIPIENT_WALLET.address);
            console.log("now has funds to make transactions!");

        } else {
            console.log("\n❌ Transaction failed!");
            console.log("Error:", sendResponse.data.error);
            console.log("Message:", sendResponse.data.message);

            if (sendResponse.data.needsFaucet) {
                console.log("\n💡 Tip:", sendResponse.data.faucetMessage);
            }
        }

    } catch (error: any) {
        console.error("\n❌ Error occurred:", error.response?.data || error.message);

        if (error.code === 'ECONNREFUSED') {
            console.log("\n💡 Make sure the server is running:");
            console.log("   npm run dev");
            console.log("   or");
            console.log("   npx ts-node crypto-stuff/suicrypto.ts");
        }
    }
}

// Alternative: Send a custom amount
async function sendCustomAmount(amountInSUI: number) {
    const amountInMIST = Math.floor(amountInSUI * 1_000_000_000);
    console.log(`\nSending ${amountInSUI} SUI (${amountInMIST} MIST)...`);

    try {
        const response = await axios.post(`${API_BASE_URL}/send-sui`, {
            privateKey: FUNDED_WALLET.privateKey,
            recipientAddress: RECIPIENT_WALLET.address,
            amount: amountInMIST
        });

        if (response.data.success) {
            console.log("✅ Sent successfully!");
            console.log("Transaction:", response.data.transactionDigest);
            console.log("Explorer:", response.data.explorerUrl);
        } else {
            console.log("❌ Failed:", response.data.message);
        }

        return response.data;
    } catch (error: any) {
        console.error("Error:", error.response?.data || error.message);
        return null;
    }
}

// Run the main function
console.log("Starting SUI Transfer...\n");
console.log("This script will send 0.0001 SUI from the funded wallet");
console.log("to your wallet so you can make transactions.\n");

sendFromFundedWallet().then(() => {
    console.log("\n======================================");
    console.log("Script completed!");
    console.log("======================================");
}).catch(console.error);

// Uncomment to send a different amount (in SUI):
// sendCustomAmount(0.1).then(console.log);  // Send 0.1 SUI
// sendCustomAmount(1.0).then(console.log);  // Send 1 SUI