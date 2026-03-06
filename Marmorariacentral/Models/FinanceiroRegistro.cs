using SQLite;
using Google.Cloud.Firestore; // Essencial para o Realtime funcionar

namespace Marmorariacentral.Models
{
    [FirestoreData] // VACINA: Diz ao Firebase que esta classe pode ser mapeada
    public class FinanceiroRegistro
    {
        [PrimaryKey]
        [FirestoreProperty("id")] // Mapeia o ID do banco
        public string Id { get; set; } = Guid.NewGuid().ToString();

        [FirestoreProperty("descricao")]
        public string Descricao { get; set; } = string.Empty;

        [FirestoreProperty("valor")]
        public double Valor { get; set; }

        [FirestoreProperty("data_vencimento")]
        public DateTime DataVencimento { get; set; }

        [FirestoreProperty("foi_pago")]
        public bool FoiPago { get; set; } = false;

        [FirestoreProperty("tipo")]
        public string Tipo { get; set; } = "Saida";

        [FirestoreProperty("is_fixo")]
        public bool IsFixo { get; set; } = false; 

        [FirestoreProperty("is_parcelado")]
        public bool IsParcelado { get; set; } = false;

        [FirestoreProperty("parcela_atual")]
        public int ParcelaAtual { get; set; } = 1;

        [FirestoreProperty("total_parcelas")]
        public int TotalParcelas { get; set; } = 1;

        [FirestoreProperty("dia_vencimento_fixo")]
        public int DiaVencimentoFixo { get; set; }

        [FirestoreProperty("pular_mes_atual")]
        public bool PularMesAtual { get; set; } = false;

        [Ignore] 
        public string DescricaoDisplay { get; set; } = string.Empty;

        [Ignore] 
        public Color StatusColor { get; set; } = Colors.Green;
    }
}