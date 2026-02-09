using Marmorariacentral.ViewModels;

namespace Marmorariacentral.Views.Orcamentos
{
    public partial class OrcamentosPage : ContentPage
    {
        private readonly OrcamentoViewModel _viewModel;

        // O MAUI injeta automaticamente a ViewModel aqui porque a registramos no MauiProgram.cs
        public OrcamentosPage(OrcamentoViewModel viewModel)
        {
            InitializeComponent();
            
            _viewModel = viewModel;
            BindingContext = _viewModel;
        }

        protected override async void OnAppearing()
        {
            base.OnAppearing();
            
            // Sempre que o usuário entrar na tela, atualizamos a lista do banco
            await _viewModel.CarregarOrcamentosCommand.ExecuteAsync(null);
        }
    }
}