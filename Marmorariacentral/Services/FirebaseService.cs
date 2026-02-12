using Google.Cloud.Firestore;
using Marmorariacentral.Models;
using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using System.Linq;
using System.IO;

namespace Marmorariacentral.Services
{
    public class FirebaseService
    {
        private FirestoreDb? _db;
        private readonly string _projectId = "marmoraria-app";
        private readonly string _keyFileName = "firebase_key.json";

        public FirebaseService()
        {
        }

        private async Task Init()
        {
            if (_db != null) return;

            try
            {
                using var stream = await FileSystem.OpenAppPackageFileAsync(_keyFileName);
                using var reader = new StreamReader(stream);
                var jsonContents = await reader.ReadToEndAsync();

                string tempPath = Path.Combine(FileSystem.CacheDirectory, _keyFileName);
                File.WriteAllText(tempPath, jsonContents);
                Environment.SetEnvironmentVariable("GOOGLE_APPLICATION_CREDENTIALS", tempPath);

                _db = await FirestoreDb.CreateAsync(_projectId);
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Erro ao inicializar Firebase: {ex.Message}");
            }
        }

        // ---------------- CLIENTES ----------------

        public async Task<List<Cliente>> GetClientesAsync()
        {
            await Init();
            var lista = new List<Cliente>();

            if (_db == null) return lista;

            try
            {
                var snapshot = await _db.Collection("clientes").GetSnapshotAsync();

                foreach (var document in snapshot.Documents)
                {
                    if (!document.Exists) continue;

                    var dict = document.ToDictionary();

                    lista.Add(new Cliente
                    {
                        Id = document.Id,
                        Nome = dict.ContainsKey("nome") ? dict["nome"]?.ToString() ?? "" : "",
                        Contato = dict.ContainsKey("contato") ? dict["contato"]?.ToString() ?? "" : "",
                        Endereco = dict.ContainsKey("endereco") ? dict["endereco"]?.ToString() ?? "" : "",
                        DataCadastro = dict.ContainsKey("data_cadastro") && dict["data_cadastro"] is Timestamp ts
                            ? ts.ToDateTime()
                            : DateTime.Now
                    });
                }
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Erro ao buscar clientes: {ex.Message}");
            }

            return lista;
        }

        public async Task SaveClienteAsync(Cliente cliente)
        {
            await Init();
            if (_db == null) return;

            var data = new Dictionary<string, object>
            {
                { "nome", cliente.Nome },
                { "contato", cliente.Contato },
                { "endereco", cliente.Endereco },
                { "data_cadastro", Timestamp.FromDateTime(cliente.DataCadastro.ToUniversalTime()) }
            };

            await _db.Collection("clientes")
                     .Document(cliente.Id)
                     .SetAsync(data);
        }

        // ---------------- PEÇAS DO ORÇAMENTO ----------------

        public async Task SavePecaOrcamentoAsync(PecaOrcamento peca)
        {
            await Init();
            if (_db == null) return;

            var data = new Dictionary<string, object>
            {
                { "cliente_id", peca.ClienteId },
                { "ambiente", peca.Ambiente },
                { "pedra_nome", peca.PedraNome },
                { "valor_m2", peca.ValorM2 },
                { "largura", peca.Largura },
                { "altura", peca.Altura },
                { "valor_total", peca.ValorTotalPeca }
            };

            await _db.Collection("orcamentos_detalhes")
                     .Document(peca.Id)
                     .SetAsync(data);
        }

        public async Task<List<PecaOrcamento>> GetPecasPorClienteAsync(string clienteId)
        {
            await Init();
            var lista = new List<PecaOrcamento>();

            if (_db == null) return lista;

            try
            {
                var query = _db.Collection("orcamentos_detalhes")
                               .WhereEqualTo("cliente_id", clienteId);

                var snapshot = await query.GetSnapshotAsync();

                foreach (var doc in snapshot.Documents)
                {
                    if (!doc.Exists) continue;

                    var dict = doc.ToDictionary();

                    lista.Add(new PecaOrcamento
                    {
                        Id = doc.Id,
                        ClienteId = clienteId,
                        Ambiente = dict.ContainsKey("ambiente") ? dict["ambiente"]?.ToString() ?? "" : "",
                        PedraNome = dict.ContainsKey("pedra_nome") ? dict["pedra_nome"]?.ToString() ?? "" : "",
                        ValorM2 = dict.ContainsKey("valor_m2") ? Convert.ToDouble(dict["valor_m2"]) : 0,
                        Largura = dict.ContainsKey("largura") ? Convert.ToDouble(dict["largura"]) : 0,
                        Altura = dict.ContainsKey("altura") ? Convert.ToDouble(dict["altura"]) : 0,
                        ValorTotalPeca = dict.ContainsKey("valor_total") ? Convert.ToDouble(dict["valor_total"]) : 0
                    });
                }
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Erro ao buscar peças: {ex.Message}");
            }

            return lista;
        }

        // ---------------- ESTOQUE ----------------

        public async Task SaveEstoqueAsync(EstoqueItem estoque)
        {
            await Init();
            if (_db == null) return;

            var data = new Dictionary<string, object>
            {
                { "nome_chapa", estoque.NomeChapa },
                { "metro_total", estoque.MetroQuadradoTotal },
                { "valor_metro", estoque.ValorPorMetro },
                { "quantidade_chapas", estoque.QuantidadeChapas }
            };

            await _db.Collection("estoque")
                     .Document(estoque.Id)
                     .SetAsync(data);
        }

        // ---------------- FINANCEIRO ----------------

        public async Task SaveFinanceiroAsync(FinanceiroRegistro financeiro)
        {
            await Init();
            if (_db == null) return;

            var data = new Dictionary<string, object>
            {
                { "descricao", financeiro.Descricao },
                { "valor", financeiro.Valor },
                { "tipo", financeiro.Tipo },
                { "data_vencimento", Timestamp.FromDateTime(financeiro.DataVencimento.ToUniversalTime()) },
                { "foi_pago", financeiro.FoiPago },
                { "is_fixo", financeiro.IsFixo },
                { "is_parcelado", financeiro.IsParcelado },
                { "parcela_atual", financeiro.ParcelaAtual },
                { "total_parcelas", financeiro.TotalParcelas },
                { "dia_vencimento_fixo", financeiro.DiaVencimentoFixo }
            };

            await _db.Collection("financeiro")
                     .Document(financeiro.Id)
                     .SetAsync(data);
        }
    }
}
