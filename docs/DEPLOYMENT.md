# CLAUSELOCK — Studionet deployment

- **Network:** GenLayer Studionet (chain ID 61999)
- **Studio import:** https://studio.genlayer.com/?import-contract=0x683A1718D50ae65b9eAfa31F06DfB06FC7C9DEED
- **Contract address provided by builder:** \`0x683A1718D50ae65b9eAfa31F06DfB06FC7C9DEED\`
- **Explorer:** https://explorer-studio.genlayer.com/address/0x683A1718D50ae65b9eAfa31F06DfB06FC7C9DEED

The read-only deployment preflight verifies source/schema and reads \`stats()\` from \`LATEST_FINAL\`, without signing a write. Signed \`create_policy\`, amendments, AI consensus, activation and rollback tests are performed separately using the [Studio acceptance guide](STUDIO_ACCEPTANCE.md).

Run \`npm install && npm run preflight\`.
