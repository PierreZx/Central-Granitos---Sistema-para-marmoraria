using Android.App;
using Android.Content;
using Android.Content.PM;
using Android.OS;
using Android.Widget;
using AndroidX.AppCompat.App;
using Android.Views;

namespace Marmorariacentral;

[Activity(Theme = "@style/Maui.SplashTheme", MainLauncher = true, NoHistory = true, 
          ConfigurationChanges = ConfigChanges.ScreenSize | ConfigChanges.Orientation | ConfigChanges.UiMode)]
public class SplashActivity : AppCompatActivity
{
    protected override void OnCreate(Bundle? savedInstanceState) // Adicionado o ? para corrigir o erro CS8765
    {
        base.OnCreate(savedInstanceState);
        
        // Esconde a barra de status
        if (Window != null)
        {
            Window.AddFlags(WindowManagerFlags.Fullscreen);
        }

        // Tenta carregar o layout. Se o Resource.Layout não aparecer, usamos o ID direto
        SetContentView(Resource.Layout.splash_layout);

        var videoView = FindViewById<VideoView>(Resource.Id.videoViewIntro);
        
        if (videoView != null)
        {
            // Caminho do vídeo. O nome "intro" deve ser o nome do arquivo MP4 na pasta raw
            string videoPath = $"android.resource://{PackageName}/raw/intro";
            videoView.SetVideoPath(videoPath);

            videoView.Completion += (s, e) => {
                StartActivity(new Intent(this, typeof(MainActivity)));
                Finish();
            };

            videoView.Start();
        }
        else
        {
            // Se o vídeo falhar por algum motivo, vai direto para o app para não travar o usuário
            StartActivity(new Intent(this, typeof(MainActivity)));
            Finish();
        }
    }
}