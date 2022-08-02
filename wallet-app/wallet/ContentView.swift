
import SwiftUI
import FirebaseAuth

class AppViewModel: ObservableObject {
    
    let auth = Auth.auth()
    
    @Published var signedIn = false
    
//    var loggedIn: Binding<Bool>
    
//    public init(loggedIn: Binding<Bool>){
//        self.loggedIn.wrappedValue = isSignedIn
//    }
    
    var isSignedIn: Bool {
        return auth.currentUser != nil
    }
    
    func signIn(email: String, password: String, loggedIn: Binding<Bool>, network: Network){
        auth.signIn(withEmail: email, password: password){ [weak self] result, error in
            guard result != nil, error == nil else{
                return
            }
            //Success
            DispatchQueue.main.async{ [self] in
                self?.signedIn = true
                loggedIn.wrappedValue = true
                network.email = email
                network.getAds()
                
            }
        }
    }
    
    func signUp(email: String, password: String, loggedIn: Binding<Bool>){
        auth.createUser(withEmail: email, password: password){ [weak self] result, error in
            guard result != nil, error == nil else{
                return
            }
            //Success
            DispatchQueue.main.async{
                self?.signedIn = true
                loggedIn.wrappedValue = true
                let user = User(email: email)
                user.registerUser()
            }
        }
    }
    
    func signOut(loggedIn: Binding<Bool>){
        try? auth.signOut()
        self.signedIn = false
        loggedIn.wrappedValue = false
    }
}

struct ContentView: View {
    @EnvironmentObject var viewModel: AppViewModel
    @EnvironmentObject var network: Network
    @State private var loggedIn: Bool = false
    @Environment(\.scenePhase) var scenePhase
    
    var body: some View {
        
        NavigationView {
            if loggedIn{
                
                TabView{
                    ScrollView{
                        VStack(spacing: 35){
                            HeaderView()
                            AsyncImage(url: URL(string: network.ad.url)) { image in
                                image
                                    .resizable()
                                    .scaledToFit()
                                    .frame(width: 300, height: 100)
                                } placeholder: {
                                    Color.gray.opacity(0.1)
                                }
                          
                            CardListView()
                            BalanceView()
                            TransferMoneyView()
                       
                            
                           
                        }.padding(.top,0)
                            .padding(.leading,25)
                            .padding(.trailing,25)
                            
                    }
                    .padding(.top,0)
                    .tabItem{
                        Image(systemName: "star")
                    }
                    VStack{
                        SettingsView()
                        Button("Signout") {
                            viewModel.signOut(loggedIn: $loggedIn)
                        }.foregroundColor(.white)
                            .frame(width: 300, height: 50)
                            .background(Color.blue)
                            .cornerRadius(10)
                    }.tabItem{
                        Image(systemName: "gear")
                    }
                    
        
                }.onAppear{
                    network.email = viewModel.auth.currentUser?.email ?? ""
                    network.getAds()
                }
                
            } else{
                signInView(loggedIn: $loggedIn)
            }
        }
        .padding(.top,0)
        .onAppear{
//            viewModel.signedIn = viewModel.isSignedIn
            loggedIn = viewModel.isSignedIn
        }
    }
}

struct signInView: View {
    @State private  var email = ""
    @State private var password = ""
    @EnvironmentObject var viewModel: AppViewModel
    @Binding var loggedIn: Bool
    @EnvironmentObject var network: Network
    
    var body: some View {
        ZStack {
            Color.blue
                .ignoresSafeArea()
            Circle()
                .scale(1.7)
                .foregroundColor(.white.opacity(0.15))
            Circle()
                .scale(1.35)
                .foregroundColor(.white)
            
            VStack {
                Text("Login")
                    .font(.largeTitle)
                    .bold()
                    .padding()
                
                TextField("Email Address", text: $email)
                    .disableAutocorrection(true)
                    .autocapitalization(.none)
                    .padding()
                    .frame(width: 300, height: 50)
                    .background(Color.black.opacity(0.05))
                    .cornerRadius(10)
                    .border(.red, width: CGFloat(0))
                
                
                SecureField("Password", text: $password)
                    .padding()
                    .frame(width: 300, height: 50)
                    .background(Color.black.opacity(0.05))
                    .cornerRadius(10)
                    .border(.red, width: CGFloat(0))
                
                Button("Login") {
                    guard !email.isEmpty, !password.isEmpty else {
                        return
                    }
                    viewModel.signIn(email: email, password: password, loggedIn: $loggedIn, network: network)
                }
                .foregroundColor(.white)
                .frame(width: 300, height: 50)
                .background(Color.blue)
                .cornerRadius(10)
                
                NavigationLink("Create Account", destination: signUpView(loggedIn: $loggedIn)).padding()
                
            }
        }.navigationBarHidden(true)
    }
}


struct signUpView: View {
    @State private  var email = ""
    @State private var password = ""
    @EnvironmentObject var viewModel: AppViewModel
    @Binding var loggedIn: Bool
    
    var body: some View {
        ZStack {
            Color.green
                .ignoresSafeArea()
            Circle()
                .scale(1.7)
                .foregroundColor(.white.opacity(0.15))
            Circle()
                .scale(1.35)
                .foregroundColor(.white)
            
            VStack {
                Text("Sign Up")
                    .font(.largeTitle)
                    .bold()
                    .padding()
                
                TextField("Email Address", text: $email)
                    .disableAutocorrection(true)
                    .autocapitalization(.none)
                    .padding()
                    .frame(width: 300, height: 50)
                    .background(Color.black.opacity(0.05))
                    .cornerRadius(10)
                    .border(.red, width: CGFloat(0))
                
                
                SecureField("Password", text: $password)
                    .padding()
                    .frame(width: 300, height: 50)
                    .background(Color.black.opacity(0.05))
                    .cornerRadius(10)
                    .border(.red, width: CGFloat(0))
                
                Button("Create Account") {
                    guard !email.isEmpty, !password.isEmpty else {
                        return
                    }
                    viewModel.signUp(email: email, password: password, loggedIn: $loggedIn)
                }
                .foregroundColor(.white)
                .frame(width: 300, height: 50)
                .background(Color.green)
                .cornerRadius(10)
                
               
            }
        }
    }
}


struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
            .environmentObject(Wallet())
            
    }
}
