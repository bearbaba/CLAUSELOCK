import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {createClient} from 'genlayer-stable';
import {studionet} from 'genlayer-stable/chains';
import {TransactionHashVariant} from 'genlayer-stable/types';

const address='0x683A1718D50ae65b9eAfa31F06DfB06FC7C9DEED';
const client=createClient({chain:studionet});
const code=readFileSync('contracts/clauselock.py','utf8');
const normalize=s=>s.replace(/\r\n/g,'\n').split('\n').map(x=>x.replace(/\s+$/,'')).join('\n').trimEnd();
const hash=s=>createHash('sha256').update(s,'utf8').digest('hex');
const expected=[
  'create_policy','propose_amendment','evaluate_amendment','activate_amendment',
  'cancel_proposal','archive_policy','get_policy','get_proposal','get_version',
  'activation_eligibility','stats'
];

console.log('NETWORK: GenLayer Studionet 61999');
console.log('CONTRACT:',address);
const deployed=await client.getContractCode(address);
if(typeof deployed!=='string'||!deployed.includes('class ClauseLock(gl.Contract)'))
 throw Error('No deployed ClauseLock source at given address');
console.log('LOCAL_SHA256:',hash(code));
console.log('DEPLOYED_SHA256:',hash(deployed));
console.log('SOURCE_NORMALIZED_MATCH:',normalize(code)===normalize(deployed));
if(normalize(code)!==normalize(deployed))throw Error('Deployed source differs from current repository');
const schema=await client.getContractSchema(address);
const methods=schema?.methods||{};
const missing=expected.filter(x=>!Object.hasOwn(methods,x));
if(missing.length)throw Error('Missing deployed methods: '+missing.join(', '));
console.log('CONSTRUCTOR:',JSON.stringify(schema.ctor));
console.log('METHODS:',Object.keys(methods).join(', '));
const result=await client.readContract({address,functionName:'stats',args:[],
 transactionHashVariant:TransactionHashVariant.LATEST_FINAL});
const value=typeof result==='string'?JSON.parse(result):result;
if(!Number.isSafeInteger(value?.policies)||!Number.isSafeInteger(value?.proposals))
 throw Error('Unexpected stats readback');
console.log('LATEST_FINAL_STATS:',JSON.stringify(value));
if(value.policies>=1){
 const policyRaw=await client.readContract({address,functionName:'get_policy',args:[1],
  transactionHashVariant:TransactionHashVariant.LATEST_FINAL});
 const policy=typeof policyRaw==='string'?JSON.parse(policyRaw):policyRaw;
 if(policy.id!==1||policy.owner?.toLowerCase()!=='0x4c7cb73ac8f8999af21cfc9ff4cf2333a9508dcb')
  throw Error('Policy #1 owner / readback mismatch');
 console.log('LATEST_FINAL_POLICY_1:',JSON.stringify({id:policy.id,owner:policy.owner,version:policy.version,guardrails:policy.protected_clauses?.map(x=>x.id)}));
}
if(value.proposals>=1){
 const proposalRaw=await client.readContract({address,functionName:'get_proposal',args:[1],
  transactionHashVariant:TransactionHashVariant.LATEST_FINAL});
 const proposal=typeof proposalRaw==='string'?JSON.parse(proposalRaw):proposalRaw;
 if(proposal.id!==1||proposal.policy_id!==1)throw Error('Proposal #1 ID / policy mismatch');
 console.log('LATEST_FINAL_PROPOSAL_1:',JSON.stringify({id:proposal.id,policy_id:proposal.policy_id,proposer:proposal.proposer,base_version:proposal.base_version,status:proposal.status,decision:proposal.decision}));
}
console.log('CLAUSELOCK_DEPLOYMENT_PREFLIGHT_PASS');
