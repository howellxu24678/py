#if defined(WIN32) || defined(WIN64) || defined(OS_IS_WINDOWS)
#if defined(TESTDLL_EXPORTS)
#define MACLIAPI __declspec(dllexport)
#else
#define MACLIAPI __declspec(dllimport)
#endif
#define MACLI_STDCALL __stdcall
#define MACLI_EXPORTS __declspec(dllexport)
#else
#define MACLIAPI
#define MACLI_STDCALL
#define MACLI_EXPORTS
#if !defined __int64
#define __int64 long long
#endif
#endif

#include <string>


struct Server 
{
	char szIp[50];
	int	 nPort;
};

class NewLoginInfo
{
public:
	NewLoginInfo() 
	{
		int j = 0;
		memset(this, 0, sizeof(*this));
	}

public:

	char	account[50];			//账号
	char	accountName[50];		//账号名称 SendMsg的时候用
	char	password[50];
	int		accountType;			//账号类型
	int		autoReconnect;			//是否自动重连
	int		serverCount;			//服务器数量
	Server	servers[10];			//服务器
};

typedef void (* Fun_OnMsgPtr)(const char *msg, int len, const char *account, void *param);


Fun_OnMsgPtr  gCallBackFunPtr = NULL;
void* gCallBackParam = NULL;

#ifdef __cplusplus
extern "C"
{
#endif

	////初始化/清理
	//MACLIAPI int MACLI_STDCALL add(int x, int y);
	//MACLIAPI int MACLI_STDCALL sub(int x, int y);

	

MACLIAPI int MACLI_STDCALL AxE_Init(void*             parentHwnd, 
		int            notifyMsg, 
		Fun_OnMsgPtr    funPtr, 
		void            *callBackParam);

MACLIAPI int MACLI_STDCALL AxE_NewMultiLogin(NewLoginInfo *infos);

MACLIAPI int MACLI_STDCALL AxE_SendMsg(const char *account, 
		const void *msg, 
		int len);




#ifdef __cplusplus
}
#endif