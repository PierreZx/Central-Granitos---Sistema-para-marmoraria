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
            // A inicialização real ocorre no Init
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

        // --- SALVAR NO ESTOQUE ---
        public async Task SaveEstoqueAsync(EstoqueItem item)
        {
            await Init();
            if (_db == null) return;

            DocumentReference docRef = _db.Collection("estoque").Document(item.Id);
            
            var data = new Dictionary<string, object>
            {
                { "nome", item.NomeChapa },
                { "quantidade", item.QuantidadeChapas },
                { "metros", item.MetroQuadradoTotal },
                { "preco_m2", item.ValorPorMetro }
            };

            await docRef.SetAsync(data);
        }

        // --- SALVAR ORÇAMENTO ---
        public async Task SaveOrcamentoAsync(Orcamento orcamento)
        {
            await Init();
            if (_db == null) return;

            DocumentReference docRef = _db.Collection("orcamentos").Document(orcamento.Id);

            var data = new Dictionary<string, object>
            {
                { "nome_cliente", orcamento.NomeCliente },
                { "contato", orcamento.Contato },
                { "valor_total", orcamento.ValorTotal },
                { "status", orcamento.Status },
                { "data_criacao", Timestamp.FromDateTime(orcamento.DataCriacao.ToUniversalTime()) }
            };

            await docRef.SetAsync(data);
        }

        // --- SALVAR FINANCEIRO (CORRIGIDO PARA FIRESTORE) ---
        public async Task SaveFinanceiroAsync(FinanceiroRegistro item)
        {
            await Init();
            if (_db == null) return;

            // Criamos a referência na coleção "financeiro" usando o ID do registro
            DocumentReference docRef = _db.Collection("financeiro").Document(item.Id);

            var data = new Dictionary<string, object>
            {
                { "descricao", item.Descricao },
                { "valor", item.Valor },
                { "data_vencimento", Timestamp.FromDateTime(item.DataVencimento.ToUniversalTime()) },
                { "foi_pago", item.FoiPago },
                { "tipo", item.Tipo },
                { "is_fixo", item.IsFixo },
                { "is_parcelado", item.IsParcelado },
                { "parcela_atual", item.ParcelaAtual },
                { "total_parcelas", item.TotalParcelas },
                { "dia_fixo", item.DiaVencimentoFixo }
            };

            await docRef.SetAsync(data);
        }

        public async Task SaveClienteAsync(Cliente cliente)
        {
            await Init();
            if (_db == null) return;

            DocumentReference docRef = _db.Collection("clientes").Document(cliente.Id);

            var data = new Dictionary<string, object>
            {
                { "nome", cliente.Nome },
                { "contato", cliente.Contato },
                { "endereco", cliente.Endereco },
                { "data_cadastro", Timestamp.FromDateTime(cliente.DataCadastro.ToUniversalTime()) }
            };

            await docRef.SetAsync(data);
        }

        // --- RESETAR COLEÇÃO ---
        public async Task ResetCollectionAsync(string collectionName)
        {
            await Init();
            if (_db == null) return;

            CollectionReference collection = _db.Collection(collectionName);
            QuerySnapshot snapshot = await collection.GetSnapshotAsync();

            foreach (DocumentSnapshot document in snapshot.Documents)
            {
                await document.Reference.DeleteAsync();
            }
        }
    }
}