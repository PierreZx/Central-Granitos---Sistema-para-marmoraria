using SQLite;

namespace Marmorariacentral.Models
{
    public class PecaOrcamento
    {
        [PrimaryKey]
        public string Id { get; set; } = Guid.NewGuid().ToString();
        
        [Indexed] 
        public string ClienteId { get; set; } = string.Empty;
        
        // --- DADOS BÁSICOS ---
        public string Ambiente { get; set; } = string.Empty;
        public string PedraNome { get; set; } = string.Empty;
        public double ValorM2 { get; set; }
        public double ValorMetroLinear { get; set; }
        public int Quantidade { get; set; } = 1;
        public bool UsarMultiplicador { get; set; }
        public double ValorTotalPeca { get; set; }

        // --- MEDIDAS DAS PEÇAS (P1, P2 e P3) ---
        public double Largura { get; set; } // P1
        public double Altura { get; set; }  // P1
        
        public double LarguraP2 { get; set; }
        public double AlturaP2 { get; set; }
        public string LadoP2 { get; set; } = "Esquerda";

        public double LarguraP3 { get; set; }
        public double AlturaP3 { get; set; }
        public string LadoP3 { get; set; } = "Direita";

        // --- ACABAMENTOS: RODOBANCA (P1, P2, P3) ---
        public double RodobancaP1Esquerda { get; set; }
        public double RodobancaP1Direita { get; set; }
        public double RodobancaP1Frente { get; set; }
        public double RodobancaP1Tras { get; set; }

        public double RodobancaP2Esquerda { get; set; }
        public double RodobancaP2Direita { get; set; }
        public double RodobancaP2Frente { get; set; }
        public double RodobancaP2Tras { get; set; }

        public double RodobancaP3Esquerda { get; set; }
        public double RodobancaP3Direita { get; set; }
        public double RodobancaP3Frente { get; set; }
        public double RodobancaP3Tras { get; set; }

        // --- ACABAMENTOS: SAIA (P1, P2, P3) ---
        public double SaiaP1Esquerda { get; set; }
        public double SaiaP1Direita { get; set; }
        public double SaiaP1Frente { get; set; }
        public double SaiaP1Tras { get; set; }

        public double SaiaP2Esquerda { get; set; }
        public double SaiaP2Direita { get; set; }
        public double SaiaP2Frente { get; set; }
        public double SaiaP2Tras { get; set; }

        public double SaiaP3Esquerda { get; set; }
        public double SaiaP3Direita { get; set; }
        public double SaiaP3Frente { get; set; }
        public double SaiaP3Tras { get; set; }

        // --- RECORTES (BOJO E COOKTOP) ---
        public bool TemBojo { get; set; }
        public string PecaDestinoBojo { get; set; } = "P1";
        public double LarguraBojo { get; set; }
        public double AlturaBojo { get; set; }
        public double BojoX { get; set; }

        public bool TemCooktop { get; set; }
        public string PecaDestinoCooktop { get; set; } = "P1";
        public double LarguraCooktop { get; set; }
        public double AlturaCooktop { get; set; }
        public double CooktopX { get; set; }
    }
}