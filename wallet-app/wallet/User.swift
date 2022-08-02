
import Foundation


struct User {
    var email: String
    
    init(email: String) {
        self.email = email
    }
    
    func registerUser(){
        let data = "?email=\(self.email)"
        apiCall(url: "register-user", data: data)
    }

    func apiCall(url:String, data: String){
//        guard let jsonData = jsonString.data(using: .utf8) else { return }

        // Send request
        guard let url = URL(string: "https://wallet-backend-dora.herokuapp.com/api/\(url)\(data)") else {return}
            
        let request = URLRequest(url: url)
        

//        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
       

        let task = URLSession.shared.dataTask(with: request) { (data, response, error) in
            if let error = error {
                print(error)
            }
        }
        task.resume()
    }
}
