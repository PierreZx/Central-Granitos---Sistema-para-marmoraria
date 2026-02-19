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

        public FirebaseService() { }

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
                { "valor_ml", peca.ValorMetroLinear },
                { "quantidade", peca.Quantidade },
                { "usar_multiplicador", peca.UsarMultiplicador },
                { "valor_total", peca.ValorTotalPeca },
                { "largura_p1", peca.Largura },
                { "altura_p1", peca.Altura },
                { "largura_p2", peca.LarguraP2 },
                { "altura_p2", peca.AlturaP2 },
                { "lado_p2", peca.LadoP2 },
                { "largura_p3", peca.LarguraP3 },
                { "altura_p3", peca.AlturaP3 },
                { "lado_p3", peca.LadoP3 },
                { "rb_p1_esq", peca.RodobancaP1Esquerda }, { "rb_p1_dir", peca.RodobancaP1Direita },
                { "rb_p1_frente", peca.RodobancaP1Frente }, { "rb_p1_tras", peca.RodobancaP1Tras },
                { "rb_p2_esq", peca.RodobancaP2Esquerda }, { "rb_p2_dir", peca.RodobancaP2Direita },
                { "rb_p2_frente", peca.RodobancaP2Frente }, { "rb_p2_tras", peca.RodobancaP2Tras },
                { "rb_p3_esq", peca.RodobancaP3Esquerda }, { "rb_p3_dir", peca.RodobancaP3Direita },
                { "rb_p3_frente", peca.RodobancaP3Frente }, { "rb_p3_tras", peca.RodobancaP3Tras },
                { "saia_p1_esq", peca.SaiaP1Esquerda }, { "saia_p1_dir", peca.SaiaP1Direita },
                { "saia_p1_frente", peca.SaiaP1Frente }, { "saia_p1_tras", peca.SaiaP1Tras },
                { "saia_p2_esq", peca.SaiaP2Esquerda }, { "saia_p2_dir", peca.SaiaP2Direita },
                { "saia_p2_frente", peca.SaiaP2Frente }, { "saia_p2_tras", peca.SaiaP2Tras },
                { "saia_p3_esq", peca.SaiaP3Esquerda }, { "saia_p3_dir", peca.SaiaP3Direita },
                { "saia_p3_frente", peca.SaiaP3Frente }, { "saia_p3_tras", peca.SaiaP3Tras },
                { "tem_bojo", peca.TemBojo }, { "bojo_destino", peca.PecaDestinoBojo },
                { "bojo_larg", peca.LarguraBojo }, { "bojo_alt", peca.AlturaBojo }, { "bojo_x", peca.BojoX },
                { "tem_cooktop", peca.TemCooktop }, { "cooktop_destino", peca.PecaDestinoCooktop },
                { "cooktop_larg", peca.LarguraCooktop }, { "cooktop_alt", peca.AlturaCooktop }, { "cooktop_x", peca.CooktopX }
            };

            await _db.Collection("orcamentos_detalhes").Document(peca.Id).SetAsync(data);
        }

        public async Task<List<PecaOrcamento>> GetPecasPorClienteAsync(string clienteId)
        {
            await Init();
            var lista = new List<PecaOrcamento>();
            if (_db == null) return lista;

            try
            {
                var query = _db.Collection("orcamentos_detalhes").WhereEqualTo("cliente_id", clienteId);
                var snapshot = await query.GetSnapshotAsync();

                foreach (var doc in snapshot.Documents)
                {
                    if (!doc.Exists) continue;
                    var d = doc.ToDictionary();

                    lista.Add(new PecaOrcamento
                    {
                        Id = doc.Id,
                        ClienteId = clienteId,
                        Ambiente = d.ContainsKey("ambiente") ? d["ambiente"]?.ToString() ?? "" : "",
                        PedraNome = d.ContainsKey("pedra_nome") ? d["pedra_nome"]?.ToString() ?? "" : "",
                        ValorM2 = d.ContainsKey("valor_m2") ? Convert.ToDouble(d["valor_m2"]) : 0,
                        ValorMetroLinear = d.ContainsKey("valor_ml") ? Convert.ToDouble(d["valor_ml"]) : 0,
                        Quantidade = d.ContainsKey("quantidade") ? Convert.ToInt32(d["quantidade"]) : 1,
                        UsarMultiplicador = d.ContainsKey("usar_multiplicador") && Convert.ToBoolean(d["usar_multiplicador"]),
                        ValorTotalPeca = d.ContainsKey("valor_total") ? Convert.ToDouble(d["valor_total"]) : 0,

                        // Geometria Principal e Pernas
                        Largura = d.ContainsKey("largura_p1") ? Convert.ToDouble(d["largura_p1"]) : 0,
                        Altura = d.ContainsKey("altura_p1") ? Convert.ToDouble(d["altura_p1"]) : 0,
                        LarguraP2 = d.ContainsKey("largura_p2") ? Convert.ToDouble(d["largura_p2"]) : 0,
                        AlturaP2 = d.ContainsKey("altura_p2") ? Convert.ToDouble(d["altura_p2"]) : 0,
                        LadoP2 = d.ContainsKey("lado_p2") ? d["lado_p2"]?.ToString() ?? "Esquerda" : "Esquerda",
                        LarguraP3 = d.ContainsKey("largura_p3") ? Convert.ToDouble(d["largura_p3"]) : 0,
                        AlturaP3 = d.ContainsKey("altura_p3") ? Convert.ToDouble(d["altura_p3"]) : 0,
                        LadoP3 = d.ContainsKey("lado_p3") ? d["lado_p3"]?.ToString() ?? "Direita" : "Direita",

                        // Rodobancas
                        RodobancaP1Esquerda = d.ContainsKey("rb_p1_esq") ? Convert.ToDouble(d["rb_p1_esq"]) : 0,
                        RodobancaP1Direita = d.ContainsKey("rb_p1_dir") ? Convert.ToDouble(d["rb_p1_dir"]) : 0,
                        RodobancaP1Frente = d.ContainsKey("rb_p1_frente") ? Convert.ToDouble(d["rb_p1_frente"]) : 0,
                        RodobancaP1Tras = d.ContainsKey("rb_p1_tras") ? Convert.ToDouble(d["rb_p1_tras"]) : 0,
                        RodobancaP2Esquerda = d.ContainsKey("rb_p2_esq") ? Convert.ToDouble(d["rb_p2_esq"]) : 0,
                        RodobancaP2Direita = d.ContainsKey("rb_p2_dir") ? Convert.ToDouble(d["rb_p2_dir"]) : 0,
                        RodobancaP2Frente = d.ContainsKey("rb_p2_frente") ? Convert.ToDouble(d["rb_p2_frente"]) : 0,
                        RodobancaP2Tras = d.ContainsKey("rb_p2_tras") ? Convert.ToDouble(d["rb_p2_tras"]) : 0,
                        RodobancaP3Esquerda = d.ContainsKey("rb_p3_esq") ? Convert.ToDouble(d["rb_p3_esq"]) : 0,
                        RodobancaP3Direita = d.ContainsKey("rb_p3_dir") ? Convert.ToDouble(d["rb_p3_dir"]) : 0,
                        RodobancaP3Frente = d.ContainsKey("rb_p3_frente") ? Convert.ToDouble(d["rb_p3_frente"]) : 0,
                        RodobancaP3Tras = d.ContainsKey("rb_p3_tras") ? Convert.ToDouble(d["rb_p3_tras"]) : 0,

                        // Saias
                        SaiaP1Esquerda = d.ContainsKey("saia_p1_esq") ? Convert.ToDouble(d["saia_p1_esq"]) : 0,
                        SaiaP1Direita = d.ContainsKey("saia_p1_dir") ? Convert.ToDouble(d["saia_p1_dir"]) : 0,
                        SaiaP1Frente = d.ContainsKey("saia_p1_frente") ? Convert.ToDouble(d["saia_p1_frente"]) : 0,
                        SaiaP1Tras = d.ContainsKey("saia_p1_tras") ? Convert.ToDouble(d["saia_p1_tras"]) : 0,
                        SaiaP2Esquerda = d.ContainsKey("saia_p2_esq") ? Convert.ToDouble(d["saia_p2_esq"]) : 0,
                        SaiaP2Direita = d.ContainsKey("saia_p2_dir") ? Convert.ToDouble(d["saia_p2_dir"]) : 0,
                        SaiaP2Frente = d.ContainsKey("saia_p2_frente") ? Convert.ToDouble(d["saia_p2_frente"]) : 0,
                        SaiaP2Tras = d.ContainsKey("saia_p2_tras") ? Convert.ToDouble(d["saia_p2_tras"]) : 0,
                        SaiaP3Esquerda = d.ContainsKey("saia_p3_esq") ? Convert.ToDouble(d["saia_p3_esq"]) : 0,
                        SaiaP3Direita = d.ContainsKey("saia_p3_dir") ? Convert.ToDouble(d["saia_p3_dir"]) : 0,
                        SaiaP3Frente = d.ContainsKey("saia_p3_frente") ? Convert.ToDouble(d["saia_p3_frente"]) : 0,
                        SaiaP3Tras = d.ContainsKey("saia_p3_tras") ? Convert.ToDouble(d["saia_p3_tras"]) : 0,

                        // Recortes
                        TemBojo = d.ContainsKey("tem_bojo") && Convert.ToBoolean(d["tem_bojo"]),
                        PecaDestinoBojo = d.ContainsKey("bojo_destino") ? d["bojo_destino"]?.ToString() ?? "P1" : "P1",
                        LarguraBojo = d.ContainsKey("bojo_larg") ? Convert.ToDouble(d["bojo_larg"]) : 0,
                        AlturaBojo = d.ContainsKey("bojo_alt") ? Convert.ToDouble(d["bojo_alt"]) : 0,
                        BojoX = d.ContainsKey("bojo_x") ? Convert.ToDouble(d["bojo_x"]) : 0,
                        TemCooktop = d.ContainsKey("tem_cooktop") && Convert.ToBoolean(d["tem_cooktop"]),
                        PecaDestinoCooktop = d.ContainsKey("cooktop_destino") ? d["cooktop_destino"]?.ToString() ?? "P1" : "P1",
                        LarguraCooktop = d.ContainsKey("cooktop_larg") ? Convert.ToDouble(d["cooktop_larg"]) : 0,
                        AlturaCooktop = d.ContainsKey("cooktop_alt") ? Convert.ToDouble(d["cooktop_alt"]) : 0,
                        CooktopX = d.ContainsKey("cooktop_x") ? Convert.ToDouble(d["cooktop_x"]) : 0
                    });
                }
            }
            catch (Exception ex) { System.Diagnostics.Debug.WriteLine($"Erro ao buscar peças: {ex.Message}"); }
            return lista;
        }

        public async Task DeletePecaOrcamentoAsync(string pecaId)
            {
                await Init();
                if (_db == null) return;

                try
                {
                    await _db.Collection("orcamentos_detalhes")
                            .Document(pecaId)
                            .DeleteAsync();
                }
                catch (Exception ex)
                {
                    System.Diagnostics.Debug.WriteLine($"Erro ao deletar peça no Firebase: {ex.Message}");
                }
            }


        public async Task<List<Cliente>> GetClientesAsync() { await Init(); var lista = new List<Cliente>(); if (_db == null) return lista; try { var snapshot = await _db.Collection("clientes").GetSnapshotAsync(); foreach (var document in snapshot.Documents) { if (!document.Exists) continue; var dict = document.ToDictionary(); lista.Add(new Cliente { Id = document.Id, Nome = dict.ContainsKey("nome") ? dict["nome"]?.ToString() ?? "" : "", Contato = dict.ContainsKey("contato") ? dict["contato"]?.ToString() ?? "" : "", Endereco = dict.ContainsKey("endereco") ? dict["endereco"]?.ToString() ?? "" : "", DataCadastro = dict.ContainsKey("data_cadastro") && dict["data_cadastro"] is Timestamp ts ? ts.ToDateTime() : DateTime.Now }); } } catch (Exception ex) { System.Diagnostics.Debug.WriteLine($"Erro ao buscar clientes: {ex.Message}"); } return lista; }
        public async Task SaveClienteAsync(Cliente cliente) { await Init(); if (_db == null) return; var data = new Dictionary<string, object> { { "nome", cliente.Nome }, { "contato", cliente.Contato }, { "endereco", cliente.Endereco }, { "data_cadastro", Timestamp.FromDateTime(cliente.DataCadastro.ToUniversalTime()) } }; await _db.Collection("clientes").Document(cliente.Id).SetAsync(data); }
        public async Task SaveEstoqueAsync(EstoqueItem estoque) { await Init(); if (_db == null) return; var data = new Dictionary<string, object> { { "nome_chapa", estoque.NomeChapa }, { "metro_total", estoque.MetroQuadradoTotal }, { "valor_metro", estoque.ValorPorMetro }, { "quantidade_chapas", estoque.QuantidadeChapas } }; await _db.Collection("estoque").Document(estoque.Id).SetAsync(data); }
        public async Task SaveFinanceiroAsync(FinanceiroRegistro financeiro) { await Init(); if (_db == null) return; var data = new Dictionary<string, object> { { "descricao", financeiro.Descricao }, { "valor", financeiro.Valor }, { "tipo", financeiro.Tipo }, { "data_vencimento", Timestamp.FromDateTime(financeiro.DataVencimento.ToUniversalTime()) }, { "foi_pago", financeiro.FoiPago }, { "is_fixo", financeiro.IsFixo }, { "is_parcelado", financeiro.IsParcelado }, { "parcela_atual", financeiro.ParcelaAtual }, { "total_parcelas", financeiro.TotalParcelas }, { "dia_vencimento_fixo", financeiro.DiaVencimentoFixo } }; await _db.Collection("financeiro").Document(financeiro.Id).SetAsync(data); }
    }
}