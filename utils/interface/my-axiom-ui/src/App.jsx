import { useState } from 'react'

import './App.css'
import data from './axiom_data.json';


function App() {
  const [axioms, setAxioms] = useState(data);

  const toggle = (name) => {
  setAxioms(axioms.map(item =>
    item.name === name ? { ...item, active: !item.active } : item
  ));
  };

  const translateSymbol = (op) => {
  const ops = {
    "AND": "∧",
    "OR": "∨",
    "IMPL": "→",
    "BUILDING_FACT": "→",
    "NOT": "¬",
    "EQUIV": "≡"
  };
  return ops[op] || op;
};

  return (
    <ul>
      {axioms.map(item => (
        <li key={item.name}>
            
          <strong>{item.name}</strong> — {item.axiom.left} {translateSymbol(item.axiom.main_op)} {item.axiom.right}
          <span> ({item.active ? "active" : "inactive"})</span>
          <input
              type="checkbox"
              checked={item.active}
              onChange={() => toggle(item.name)}
            />
        </li>
      ))}
    </ul>
  );
}

export default App
