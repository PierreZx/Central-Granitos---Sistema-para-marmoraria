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

        // ==========================================
        // SINCRONIZAÇÃO FINANCEIRA (Versão Unificada)
        // ==========================================

        /// <summary>
        /// Salva ou atualiza um registro de caixa no Firestore.
        /// </summary>
        public async Task SaveFinanceiroAsync(FinanceiroRegistro financeiro)
        {
            await Init();
            if (_db == null) return;

            var data = new Dictionary<string, object>
            {
                { "id", financeiro.Id },
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

            await _db.Collection("financeiro").Document(financeiro.Id).SetAsync(data);
        }

        /// <summary>
        /// Deleta um registro financeiro da nuvem.
        /// </summary>
        public async Task DeleteFinanceiroAsync(string id)
        {
            await Init();
            if (_db == null) return;

            try
            {
                await _db.Collection("financeiro").Document(id).DeleteAsync();
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Erro ao deletar financeiro no Firebase: {ex.Message}");
            }
        }

        /// <summary>
        /// Busca todos os registros financeiros da nuvem para sincronização.
        /// </summary>
        public async Task<List<FinanceiroRegistro>> GetAllFinanceiroAsync()
        {
            await Init();
            var lista = new List<FinanceiroRegistro>();
            if (_db == null) return lista;

            try
            {
                var snapshot = await _db.Collection("financeiro").GetSnapshotAsync();
                foreach (var doc in snapshot.Documents)
                {
                    if (!doc.Exists) continue;
                    var d = doc.ToDictionary();

                    lista.Add(new FinanceiroRegistro
                    {
                        Id = doc.Id,
                        Descricao = d.ContainsKey("descricao") ? d["descricao"]?.ToString() ?? "" : "",
                        Valor = d.ContainsKey("valor") ? Convert.ToDouble(d["valor"]) : 0,
                        Tipo = d.ContainsKey("tipo") ? d["tipo"]?.ToString() ?? "Saida" : "Saida",
                        DataVencimento = d.ContainsKey("data_vencimento") && d["data_vencimento"] is Timestamp ts ? ts.ToDateTime() : DateTime.Now,
                        FoiPago = d.ContainsKey("foi_pago") && Convert.ToBoolean(d["foi_pago"]),
                        IsFixo = d.ContainsKey("is_fixo") && Convert.ToBoolean(d["is_fixo"]),
                        IsParcelado = d.ContainsKey("is_parcelado") && Convert.ToBoolean(d["is_parcelado"]),
                        ParcelaAtual = d.ContainsKey("parcela_atual") ? Convert.ToInt32(d["parcela_atual"]) : 1,
                        TotalParcelas = d.ContainsKey("total_parcelas") ? Convert.ToInt32(d["total_parcelas"]) : 1,
                        DiaVencimentoFixo = d.ContainsKey("dia_vencimento_fixo") ? Convert.ToInt32(d["dia_vencimento_fixo"]) : 0
                    });
                }
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Erro ao baixar dados do Firebase: {ex.Message}");
            }
            return lista;
        }
    }
}