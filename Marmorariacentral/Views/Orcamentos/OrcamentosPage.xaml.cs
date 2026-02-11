using Marmorariacentral.ViewModels;

namespace Marmorariacentral.Views.Orcamentos
{
    public partial class OrcamentosPage : ContentPage
    {
        private readonly OrcamentoViewModel _viewModel;

        public OrcamentosPage(OrcamentoViewModel viewModel)
        {
            InitializeComponent();
            
            _viewModel = viewModel;
            BindingContext = _viewModel;
        }

        protected override async void OnAppearing()
        {
            base.OnAppearing();
            
            if (_viewModel != null)
            {
                // O comando foi renomeado para CarregarDados para ser mais abrangente
                await _viewModel.CarregarDadosCommand.ExecuteAsync(null);
            }
        }
    }
}