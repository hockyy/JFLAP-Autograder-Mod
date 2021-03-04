#include <iostream>
#include <regex>
using namespace std;


#define rep(i, a, b) for(int i = a; i < (b); ++i)
#define trav(a, x) for(auto& a : x)
#define all(x) begin(x), end(x)
#define sz(x) (int)(x).size()

void demo() {

    if (regex_match ("subject", regex("(sub)(.*)") ))
        cout << "string literal matched\n";

    const char cstr[] = "subject";
    string s ("subject");
    regex e ("(sub)(.*)");

    if (regex_match (s, e))
        cout << "string object matched\n";

    if ( regex_match ( s.begin(), s.end(), e ) )
        cout << "range matched\n";

    cmatch cm;    // same as match_results<const char*> cm;
    regex_match (cstr, cm, e);
    cout << "string literal with " << cm.size() << " matches\n";
    trav(cur, cm) cout << cur << endl;

    smatch sm;    // same as match_results<string::const_iterator> sm;
    regex_match (s, sm, e);
    cout << "string object with " << sm.size() << " matches\n";

    regex_match ( s.cbegin(), s.cend(), sm, e);

    trav(cur, sm) cout << cur << endl;

    cout << "range with " << sm.size() << " matches\n";

    // using explicit flags:
    regex_match ( cstr, cm, e, regex_constants::match_default );

    cout << "the matches were: ";
    for (unsigned i = 0; i < cm.size(); ++i) {
        cout << "[" << cm[i] << "] ";
    }

    cout << endl;
}

string verdict[] = {"reject", "accept"};

int main() {

    ios_base::sync_with_stdio(0);
    cin.tie(0);
    cout.tie(0);
    string ss;
    while(cin >> ss) {
        string pattern = R"((\d*)000(\d*)011(\d*))";
        string pattern2 = R"((\d*)011(\d*)000(\d*))";
        cout << ss << " ";
        bool ans = regex_match(ss, regex(pattern)) || regex_match(ss, regex(pattern2));
        cout << verdict[ans] << endl;
    }
}
