import React from "react";
//import { useNavigate } from 'react-router-dom';
// import TextType from "../animation/texttype/TextType";
//import Silk from "../components/DarkVeil/DarkVeil";
// import DarkVeil from '../components/DarkVeil/DarkVeil';
import "./styles.js"
import { Container, Main } from "./styles.js";
// Componente principal
function Home() {
  // const navigate = useNavigate();
  return (
    <Main>
       <Container>
      <div>
        <h1>OPTMUS-IA</h1>
         <h6>Plataforma de analise estratégica e gestão empresarial, que combina dasboards em
          tempo real, análise de mercado, insights automatizda com IA e ferramentas de monitoramento
          finacneiro e operacional
        </h6>
      </div>
      <div className="Container-2">
      </div>
    </Container>
    </Main>
  );
}

export default Home;
