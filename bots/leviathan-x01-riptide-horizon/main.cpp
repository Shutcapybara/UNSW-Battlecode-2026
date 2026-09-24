// Leviathan / Riptide: fresh C++ policy; geometry informed by Leviathan v07.
#include <iostream>
#include <sstream>
#include "planner.h"
vector<std::string> words() {
    std::string line;
    while(std::getline(std::cin,line)) {
        line=line.substr(0,line.find('#'));std::istringstream stream(line);
        vector<std::string> out;std::string token;while(stream>>token)out.push_back(token);
        if(!out.empty())return out;
    }
    return {};
}
int main() {
    // Keep the standard stream buffer: one stdout flush per turn in the judge.
    auto start=words();if(start.empty())return 0;
    World w;w.id=std::stoi(start[1]);w.team=words()[1][0];auto dimensions=words();
    w.setup(std::stoi(dimensions[1]),std::stoi(dimensions[2]));w.limit=std::stoi(words()[1]);
    while(true) {
        auto line=words();if(line.empty()||line[0]=="ENDGAME")break;
        w.round=std::stoi(line[1]);words();w.length=std::stoi(words()[1]);w.units=std::stoi(words()[1]);
        int messages=std::stoi(words()[1]);for(int i=0;i<messages;i++)w.hear(std::stoull(words()[0]));
        auto first=words();if(first[0]=="ECHOES")first=words();
        for(int i=0;i<49;i++) {
            auto t=i?words():first;int c=std::stoi(t[1])*w.w+std::stoi(t[0]);
            if(i==24)w.head=c;auto &tile=w.tiles[c];tile.seen=w.round;
            tile.pearl=t[2]=="1"?w.round:-1000;int countdown=std::stoi(t[3]);
            tile.bed=countdown>=0;tile.due=tile.bed?w.round+countdown:-1000;
        }
        w.parts.assign(w.n,Part{});w.enemy_heads.clear();w.ally_heads.clear();w.enemy_length.clear();
        std::map<int,int> mine;int count=std::stoi(words()[1]);
        for(int i=0;i<count;i++) {
            auto p=words();int id=std::stoi(p[1]),c=std::stoi(p[3])*w.w+std::stoi(p[2]);
            int facing=std::string(DIRS).find(p[4][0]);bool ours=p[0][0]==w.team,head=p[5]=="1";
            w.parts[c]={id,ours,head,facing};w.tiles[c].pearl=-1000;
            if(id==w.id)mine[c]=facing;
            else if(ours&&head)w.ally_heads.push_back(c);
            else if(!ours) {w.enemy_length[id]++;if(head)w.enemy_heads.push_back(c);}
        }
        int hx=w.head%w.w,hy=w.head/w.w;
        for(int r=0;r<8;r++) {auto row=words();for(int c=0;c<7;c++)
            w.learn(((hy-3+r+w.h)%w.h)*w.w+(hx-3+c+w.w)%w.w,row[c]);}
        for(int r=0;r<7;r++) {auto row=words();for(int c=0;c<8;c++)
            w.learn(w.n+((hy-3+r+w.h)%w.h)*w.w+(hx-3+c+w.w)%w.w,row[c]);}
        w.rebuild();w.reconstruct(mine);w.tiles[w.head].visits++;
        for(auto it=w.reports.begin();it!=w.reports.end();) {
            if(w.round-it->second.round>4)it=w.reports.erase(it);else ++it;
        }
        Planner planner(w);Action a=planner.decide();
        std::ostringstream out;
        if(a.split) {out<<"SPLIT 2\n";w.history.resize(w.length-2);}
        else {
            out<<"MOVE "<<a.path<<"\n";int c=w.head;
            for(char d:a.path) {int v=w.next(c,std::string(DIRS).find(d));if(v<0)break;c=v;
                w.history.insert(w.history.begin(),c);w.tiles[c].pearl=-1000;}
        }
        if(w.history.size()>2048)w.history.resize(2048);
        if(P::radio&&w.n<=4096&&w.id<1048576) {
            auto packet=w.packet(a.head,a.len);
            for(char d:std::string(DIRS))out<<"SONAR "<<d<<' '<<packet<<'\n';
        }
        out<<"INDICATOR riptide depth="<<a.depth<<" risk="<<a.risk<<" split="<<a.split<<"\nPROTOCOL 3\nENDTURN\n";
        std::cout<<out.str()<<std::flush;
    }
}
