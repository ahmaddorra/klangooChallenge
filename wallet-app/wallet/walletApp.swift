

import SwiftUI
import Firebase

@main
struct walletApp: App {
    @UIApplicationDelegateAdaptor(AppDelegate.self) var appDelegate
    @StateObject private var wallet = Wallet()
    var network = Network(email: "")
    @StateObject var twitterAPI = TwitterAPI() 
    
    var body: some Scene {
        WindowGroup {
            let viewModel = AppViewModel()
            ContentView()
                .environmentObject(viewModel)
                .environmentObject(wallet)
                .environmentObject(network)
                .environmentObject(twitterAPI)
                .onOpenURL { url in // 1
                                    guard let urlScheme = url.scheme,
                                          let callbackURL = URL(string: "\(TwitterAPI.ClientCredentials.CallbackURLScheme)://"),
                                          let callbackURLScheme = callbackURL.scheme
                                    else { return } // 2
                                
                                    guard urlScheme.caseInsensitiveCompare(callbackURLScheme) == .orderedSame
                                    else { return } // 3
                                    
                                    twitterAPI.onOAuthRedirect.send(url) // 4
                    }
        }
    }
}


class AppDelegate: NSObject, UIApplicationDelegate {
    func application(_ application: UIApplication, didFinishLaunchingWithOptions launchOptions:
                     [UIApplication.LaunchOptionsKey: Any]? = nil) -> Bool{
        FirebaseApp.configure()        
        return true
    }
}

final class Wallet: ObservableObject{
    @Published var cards = cardsData
    var selectedCard: Card{
        cards.first(where: {$0.isSelected})!
    }
}
