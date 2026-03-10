using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using CommunityToolkit.Maui.Views;
using Microsoft.Maui.ApplicationModel;
using Marmorariacentral.Models;
using Marmorariacentral.Services;
using Marmorariacentral.Views.Orcamentos;
using System.Collections.ObjectModel;
using System.Diagnostics;
using System.Linq;

namespace Marmorariacentral.ViewModels
{
    public partial class OrcamentoViewModel : ObservableObject
    {
        private readonly DatabaseService _dbService;
        private readonly FirebaseService _firebaseService;

        private ObservableCollection<Cliente> _clientes = new();
        public ObservableCollection<Cliente> Clientes
        {
            get => _clientes;
            set => SetProperty(ref _clientes, value);
        }

        public OrcamentoViewModel(DatabaseService dbService, FirebaseService firebaseService)
        {
            _dbService = dbService;
            _firebaseService = firebaseService;

            _ = CarregarDados();
        }

        [RelayCommand]
        public async Task CarregarDados()
        {
            try
            {
                // 1️⃣ Carrega clientes locais
                var listaLocal = await _dbService.GetItemsAsync<Cliente>();

                AtualizarListaUI(listaLocal);

                // 2️⃣ Tenta buscar da nuvem
                var listaFirebase = await _firebaseService.GetClientesAsync();

                if (listaFirebase == null || !listaFirebase.Any())
                    return;

                bool alterouBancoLocal = false;

                foreach (var clienteNuvem in listaFirebase)
                {
                    // verifica se já existe no SQLite
                    var existente = listaLocal.FirstOrDefault(x => x.Id == clienteNuvem.Id);

                    if (existente == null)
                    {
                        // cliente novo da nuvem
                        await _dbService.SaveItemAsync(clienteNuvem);
                        alterouBancoLocal = true;
                    }
                    else
                    {
                        // atualiza dados se mudou
                        if (existente.Nome != clienteNuvem.Nome ||
                            existente.Contato != clienteNuvem.Contato ||
                            existente.Endereco != clienteNuvem.Endereco)
                        {
                            await _dbService.SaveItemAsync(clienteNuvem);
                            alterouBancoLocal = true;
                        }
                    }
                }

                // 3️⃣ Atualiza UI apenas se mudou algo
                if (alterouBancoLocal)
                {
                    var listaAtualizada = await _dbService.GetItemsAsync<Cliente>();
                    AtualizarListaUI(listaAtualizada);
                }
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"Erro na sincronização: {ex.Message}");
            }
        }

        private void AtualizarListaUI(List<Cliente> lista)
        {
            MainThread.BeginInvokeOnMainThread(() =>
            {
                Clientes.Clear();
                foreach (var c in lista.OrderBy(x => x.Nome))
                {
                    Clientes.Add(c);
                }
            });
        }

        [RelayCommand]
        public async Task AbrirCadastroCliente()
        {
            await MainThread.InvokeOnMainThreadAsync(async () =>
            {
                try
                {
                    var popup = new CadastroClientePopup();
                    var resultado = await Shell.Current.ShowPopupAsync(popup);

                    if (resultado is Cliente novo)
                    {
                        await _dbService.SaveItemAsync(novo);

                        _ = Task.Run(async () =>
                        {
                            try { await _firebaseService.SaveClienteAsync(novo); }
                            catch (Exception ex) { Debug.WriteLine(ex.Message); }
                        });

                        await CarregarDados();
                    }
                }
                catch (Exception ex) { Debug.WriteLine(ex.Message); }
            });
        }

        [RelayCommand]
        public async Task EditarCliente(Cliente cliente)
        {
            if (cliente == null) return;

            await MainThread.InvokeOnMainThreadAsync(async () =>
            {
                var popup = new CadastroClientePopup(cliente);
                var resultado = await Shell.Current.ShowPopupAsync(popup);

                if (resultado is Cliente editado)
                {
                    await _dbService.SaveItemAsync(editado);

                    _ = Task.Run(async () =>
                    {
                        try { await _firebaseService.SaveClienteAsync(editado); }
                        catch { }
                    });

                    await CarregarDados();
                }
            });
        }

        [RelayCommand]
        public async Task ExcluirCliente(Cliente cliente)
        {
            if (cliente == null) return;

            bool confirmar = await Shell.Current.DisplayAlert(
                "Excluir",
                $"Deseja remover permanentemente o cliente {cliente.Nome}?",
                "Sim",
                "Não");

            if (!confirmar) return;

            try
            {
                // remove local
                await _dbService.DeleteItemAsync(cliente);

                // remove da nuvem
                _ = Task.Run(async () =>
                {
                    try
                    {
                        await _firebaseService.DeleteClienteAsync(cliente.Id);
                    }
                    catch (Exception ex)
                    {
                        Debug.WriteLine($"Erro ao excluir do Firebase: {ex.Message}");
                    }
                });

                await CarregarDados();
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"Erro ao excluir cliente: {ex.Message}");
            }
        }

        [RelayCommand]
        public async Task AbrirDetalhesCliente(Cliente cliente)
        {
            if (cliente == null) return;

            var navigationParameter = new Dictionary<string, object>
            {
                { "Cliente", cliente }
            };

            // CORREÇÃO: Remover o acento e usar EXATAMENTE o mesmo nome do registro
            await Shell.Current.GoToAsync("DetalhesClientePage", navigationParameter);
        }
    }
}