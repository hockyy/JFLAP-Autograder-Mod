const fs = require('fs');
let edges;
let N;

try {  
    edges = fs.readFileSync('graph.txt', 'utf8').toString();
    edges = edges.split('\r\n');
    N = edges[0]; edges.shift();
} catch(e) {
    console.log('Error:', e.stack);
}

console.log(`<automaton>`);
for (let i = 1;i <= N;i++){
    const currentChild = (`  <state id="${i}" name="q${i}"></state>`);
    console.log(currentChild);
}


for (const edge of edges){
    let trav = edge.split(" ");
    if(trav.length != 3) continue;
    const currentChild = `  <transition><from>${trav[0]}</from><to>${trav[1]}</to><read>${trav[2]}</read></transition>`;
    console.log(currentChild);
}

console.log(`</automaton>`);


