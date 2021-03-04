const xml = require('xml-parse'); // https://www.npmjs.com/package/xml-parse
const template =
`<?xml version="1.0" encoding="UTF-8" standalone="no"?><!--Created with JFLAP 7.1.--><structure>
    <type>fa</type>
    <automaton></automaton>
</structure>`;

const state = `<state id="0" name="q0"><initial/></state>`;

const transition = `<transition><from>1</from><to>3</to><read>0</read></transition>`;

const edges =
`

`

function createXML(s, ws){
    return new xml.DOM(xml.parse(s)).document.getElementsByTagName(ws)[0];
}

const automaton = createXML(template, "automaton");
automaton.appendChild(createXML(state, "state"));
// console.log(automaton);
let xmlStr = xml.stringify([automaton], 2);
console.log(xmlStr);


