# include <sig/gs_vis_graph.h>
# include <sig/sn_poly_editor.h>
# include <iostream>

class PathPlanner {

	float R;                        // disaster - R detour parameter
	GsPnt2 _pi, _pg;                // Starting point, endpoint
	GsPolygons dangerZones;         // Dangerzones loaded into the pathplanner
	GsPolygons* obstacles;          // Always containing the actual danger zones to be avoided

	char* _path;                    // The path calculated
	float _cost;                    // the cost of the most recently calculated path
	float _epsilon;					// The epsilon needed to get a valid path

	int strlen(float f)
	{   // .12345 max accuracy -> 6 mor chars needed.
		int h = 0;
		if ((int)f == 0) return 7;
		while (f > 1){ f = f / 10.0f; h++; }
		return h + 6;
	}

public:

	PathPlanner()
	{
		//std::cout << "const called" << std::endl;
		_path = new char[2];
		_path[0] = '-';
		_path[1] = '\0';
		_cost = 0.0f;
		_epsilon = 0.0f;
		dangerZones.init();
		obstacles = new GsPolygons();
	}
	~PathPlanner(){ delete[] _path; }

	void AddDangerZone(const char* polydata)
	{
		GsPolygon& p = dangerZones.push();
		p.setpoly(polydata);
		std::cout << dangerZones.size() << " "<< polydata << std::endl;
	}

	void SetDangerZones(int* ids, int n)
	{
	    std::cout << "set: "<< n << "size: " << dangerZones.size() << std::endl;
		//empty obstacles
		obstacles = new GsPolygons();
		obstacles->init();
		obstacles->size(n);

		//fill in with new polygons
		for (int i = 0; i < n; i++){
		    std::cout << ids[i] << std::endl;
		    obstacles->set(i, dangerZones[ids[i]]);
		    std::cout << ids[i] << std::endl;
        }
		// set epsilon back to 0
		_epsilon = 0.0f;
	}

	void CalculatePath()
    {
		GsVisGraph _vg;                 // The visual graph we use for path planning

		float dang = GS_TORAD(3);       // Circle resolution parameter of the visual graph
		_vg.build(obstacles, R - _epsilon, dang);

		GsPolygon detour;
		bool found = _vg.shortest_path(_pi, _pg, detour, &_cost);

		if(found)
		{
			int n = detour.size();

			int size = 3 * n;
			for (int i = 0; i < n; i++){ size += strlen(detour[i].x) + strlen(detour[i].y); }

			delete[] _path;
			_path = new char[size*2];

			int j = 0;
			for (int i = 0; i < n; i++){ j += sprintf(_path + j, "%.5f %.5f  ", detour[i].x, detour[i].y); }

		}
		else
		{
			_epsilon += R * 0.01; 		//increase epsilon
			CalculatePath();			//try again
		}

	}

	char* GetPath(){ return _path; }
	float GetCost() { return _cost; }
	float GetEpsilon() { return _epsilon; }

	void SetR(float r) { R = r; }
	void SetStartPoint(float x, float y) { _pi.set(x, y); }
	void SetEndPoint(float x, float y) { _pg.set(x, y); }
};

//Define C typed function calls for the shared library export
extern "C"
{
    PathPlanner* PP_new() { return new PathPlanner(); }
    void PP_addDangerZone(PathPlanner* p, const char* c) { p->AddDangerZone(c); }
    void PP_setDangerZones(PathPlanner* p, int* arr, int n){ p->SetDangerZones(arr, n); }
    void PP_calculatePath(PathPlanner* p){ p->CalculatePath(); }
    char* PP_getPath(PathPlanner* p) { return p->GetPath(); }
    float PP_getCost(PathPlanner* p) { return p->GetCost(); }
	float PP_getEpsilon(PathPlanner* p) { return p->GetEpsilon(); }
    void PP_setR(PathPlanner* p, float r) { p->SetR(r); }
    void PP_setStartPoint(PathPlanner* p, float x, float y) { p->SetStartPoint( x, y ); }
    void PP_setEndPoint(PathPlanner* p, float x, float y) { p->SetEndPoint( x, y ); }
}