using SQLite;
using System;
using System.Collections.Generic;

namespace Marmorariacentral.Models
{
    public class Orcamento
    {
        [PrimaryKey]
        public string Id { get; set; } = Guid.NewGuid().ToString(); // Proteção contra duplicatas offline
        
        [Indexed]
        public string NomeCliente { get; set; } = string.Empty;
        public string Contato { get; set; } = string.Empty;
        public string Endereco { get; set; } = string.Empty;
        
        public double ValorTotal { get; set; }
        public string Status { get; set; } = "Orcamento"; // Orcamento, Producao, Finalizado
        
        // Controle de Sincronia e Produção
        public bool IsSynced { get; set; } = false;
        public DateTime DataCriacao { get; set; } = DateTime.Now;
        public string EtapaProducao { get; set; } = "Novo"; // Novo, Produzindo, Finalizado
    }
}