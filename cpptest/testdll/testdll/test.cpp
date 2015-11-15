#include "test.h"
#include <Windows.h>


//MACLIAPI int MACLI_STDCALL add( int x, int y )
//{
//	return x+y;
//}
//
//MACLIAPI int MACLI_STDCALL sub( int x, int y )
//{
//	return x-y;
//}

MACLIAPI int MACLI_STDCALL AxE_Init( void* parentHwnd, int notifyMsg, Fun_OnMsgPtr funPtr, void *callBackParam )
{
	gCallBackFunPtr = funPtr;
	gCallBackParam = callBackParam;
	return 0;
}

MACLIAPI int MACLI_STDCALL AxE_NewMultiLogin( NewLoginInfo *infos )
{
	return 0;
}

MACLIAPI int MACLI_STDCALL AxE_SendMsg( const char *account, const void *msg, int len )
{
	Sleep(100);
	char szMsgSend[1024] = {0};
	memcpy(szMsgSend, msg, len);
	printf("TestDll revc the msg is:%s\n", szMsgSend);
	char szMsg[] = "callback msg";
	gCallBackFunPtr(szMsg, sizeof(szMsg), "1231212", gCallBackParam);
	return 0;
}

