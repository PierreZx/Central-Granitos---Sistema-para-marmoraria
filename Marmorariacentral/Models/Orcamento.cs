using SQLite;
using System;
using System.Collections.Generic;
using System.Text.Json;

namespace Marmorariacentral.Models
{
    public class Orcamento
    {
        [PrimaryKey]
        public string Id { get; set; } = Guid.NewGuid().ToString();

        [Indexed]
        public string NomeCliente { get; set; } = string.Empty;

        public string Contato { get; set; } = string.Empty;

        public string Endereco { get; set; } = string.Empty;

        // Número visual do orçamento (ex: 0001/2026)
        public string NumeroOrcamento { get; set; } = 
            $"{DateTime.Now.Year}-{new Random().Next(1000,9999)}";

        public double ValorTotal { get; set; }

        public string Status { get; set; } = "Orcamento";

        public bool IsSynced { get; set; } = false;

        public DateTime DataCriacao { get; set; } = DateTime.Now;

        public string EtapaProducao { get; set; } = "Novo";

        public string Observacoes { get; set; } = string.Empty;

        // 👇 Armazenamento das peças como JSON no SQLite
        public string PecasJson { get; set; } = string.Empty;

        // 👇 Propriedade não mapeada para trabalhar com lista real
        [Ignore]
        public List<PecaOrcamento> Pecas
        {
            get
            {
                if (string.IsNullOrEmpty(PecasJson))
                    return new List<PecaOrcamento>();

                return JsonSerializer.Deserialize<List<PecaOrcamento>>(PecasJson)
                       ?? new List<PecaOrcamento>();
            }
            set
            {
                PecasJson = JsonSerializer.Serialize(value);
            }
        }
    }
}