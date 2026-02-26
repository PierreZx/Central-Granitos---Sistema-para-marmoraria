using Android.App;
using Android.Content.PM;
using Android.OS;
using Android.Content;

namespace Marmorariacentral;

[Activity(
    Theme = "@style/Maui.MainTheme", 
    MainLauncher = false, 
    LaunchMode = LaunchMode.SingleTop, 
    ConfigurationChanges = ConfigChanges.ScreenSize | ConfigChanges.Orientation | ConfigChanges.UiMode | ConfigChanges.ScreenLayout | ConfigChanges.SmallestScreenSize | ConfigChanges.Density)]
public class MainActivity : MauiAppCompatActivity
{
    // Na v3 do Shiny, se você registrou .UseShiny() e .UseNotifications() 
    // no MauiProgram.cs, o Shiny se integra automaticamente ao ciclo de vida 
    // do Android através de um Init interno. 
    // Não precisamos das chamadas de "PlatformExtensions" que estão falhando.

    protected override void OnCreate(Bundle? savedInstanceState)
    {
        base.OnCreate(savedInstanceState);
        
        // Se você quiser garantir que as permissões sejam pedidas logo no início:
        if (Build.VERSION.SdkInt >= BuildVersionCodes.Tiramisu)
        {
            if (CheckSelfPermission(Android.Manifest.Permission.PostNotifications) != Permission.Granted)
            {
                RequestPermissions(new string[] { Android.Manifest.Permission.PostNotifications }, 0);
            }
        }
    }
}