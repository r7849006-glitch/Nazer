int main() {
    srand(time(NULL));
    printf("\n════════════════════════════════════════════════════════════════\n");
    printf("🌊 RAVEN STARS BLOCKCHAIN - Multi-Currency & Speed Test\n");
    printf("════════════════════════════════════════════════════════════════\n\n");

    Blockchain my_blockchain;
    init_blockchain(&my_blockchain);
    strcpy(my_blockchain.node_identifier, "rvs-node-12345");
    sleep(1);

    printf("🔄 Adding multi-cross-chain transactions (RVC, ETH, BTC, SOL)...\n");
    
    add_rvc_transaction(&my_blockchain, my_blockchain.node_identifier, "rvs-user-A", 15.0);
    add_external_transaction(&my_blockchain, "ETH", my_blockchain.node_identifier, "eth-user-B", 3.5, "EXTERNAL_TRANSFER", "eth_tx_101");
    add_external_transaction(&my_blockchain, "BTC", my_blockchain.node_identifier, "btc-user-C", 0.45, "EXTERNAL_TRANSFER", "btc_tx_202");
    add_external_transaction(&my_blockchain, "SOL", my_blockchain.node_identifier, "sol-user-D", 25.0, "EXTERNAL_TRANSFER", "sol_tx_303");

    printf("⏳ Starting Proof-of-Work & Speed Measurement...\n");
    
    clock_t start_time = clock();

    int mined_star_path[STAR_PATH_LEN];
    char mined_nonce_hash[HASH_LEN];
    proof_of_work(&my_blockchain, mined_star_path, mined_nonce_hash);

    clock_t end_time = clock();
    double cpu_time_used = ((double)(end_time - start_time)) / CLOCKS_PER_SEC;

    if (strlen(mined_nonce_hash) > 0) {
        char prev_hash[HASH_LEN];
        calculate_block_hash(&my_blockchain.chain[my_blockchain.num_blocks - 1], prev_hash);
        Block* new_block = create_block(&my_blockchain, mined_nonce_hash, prev_hash, mined_star_path, -1.0, false);
        
        printf("\n✅ Block %d mined successfully!\n", new_block->index);
        printf("   ⏱️ Mining Latency / Speed: %.4f seconds\n", cpu_time_used);
        printf("   🌊 Wave Harmony: %.3f\n", new_block->block_wave.harmony_score);
        printf("   📦 Total Transactions in Block: %d\n", new_block->num_transactions);
    } else {
        printf("❌ Mining failed.\n");
    }

    printf("\n💰 Multi-Currency Final Balances:\n");
    printf("   Node RVC: %.2f RVC\n", get_balance(&my_blockchain.balances, my_blockchain.node_identifier, "RVC"));
    printf("   User-A RVC: %.2f RVC\n", get_balance(&my_blockchain.balances, "rvs-user-A", "RVC"));
    printf("   User-B ETH: %.2f ETH\n", get_balance(&my_blockchain.balances, "eth-user-B", "ETH"));
    printf("   User-C BTC: %.4f BTC\n", get_balance(&my_blockchain.balances, "btc-user-C", "BTC"));
    printf("   User-D SOL: %.2f SOL\n", get_balance(&my_blockchain.balances, "sol-user-D", "SOL"));

    free_blockchain(&my_blockchain);
    return 0;
}
