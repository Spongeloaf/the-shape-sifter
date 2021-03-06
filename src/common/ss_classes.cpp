#include "ss_classes.h"

// The server calls this method to retrieve output parts from the client
void ClientBase::SendPartsToServer(PartList& partList)
{
	if (m_OutputLock.try_lock())
	{
		if (!m_OutputBuffer.empty())
		{
			for (auto& part : m_OutputBuffer)
			{
				// This should automagically overwrite any part in the list with new contents, or add new parts.
				partList[part.first] = std::move(part.second);
			}
			m_OutputBuffer.clear();
		}
	m_OutputLock.unlock();
	}
}

// The server call this method to send a part to this client
void ClientBase::SendPartToClient(Parts::PartInstance& part)
{
	if (m_InputLock.try_lock())
	{
		m_InputBuffer[part.m_PUID] = part;
		m_InputLock.unlock();
	}
}

// The client calls this method to retrieve parts from the Input buffer, which were sent from the server.
std::optional<Parts::PartInstance> ClientBase::GetPartFromInputBuffer()
{
	// We want this to block because if we cannot lock the input buffer, there's no point in carrying on.
	LOCK_GUARD(m_InputLock)

	if (m_InputBuffer.size() != 0)
	{
		Parts::PartInstance part = m_InputBuffer.begin()->second;
		m_InputBuffer.erase(m_InputBuffer.begin());
		return std::move(part);
	}
	return {};
}

// The client calls this method to place parts in the output buffer, for retrieval by the server.
void ClientBase::PutPartInOutputBuffer(Parts::PartInstance& part) 
{
	m_OutputLock.lock();
	m_OutputBuffer.insert(std::make_pair(part.m_PUID, std::move(part)));
	m_OutputLock.unlock();
}

void ClientBase::CopyServerPartListToClient(PartList& partList)
{
	if (m_InputLock.try_lock())
	{
		m_InputBuffer = partList;
		m_InputLock.unlock();
	}
}

void ClientBase::TimeStampPart(Parts::PartInstance& part) 
{
	auto time = std::chrono::system_clock::now();
	
	if (m_clientName == kNamePhotophile)
	{
		part.m_TimePhile = time;
	}

	else if (m_clientName == kNameMtMind)
	{
		part.m_TimeMTM = time;
	}

	else if (m_clientName == kNameClassiFist)
	{
		part.m_TimeCF = time;
	}

	else if (m_clientName == kNameBeltBuckle)
	{
		part.m_TimeBB = time;
	}
}

unsigned int ClientBase::RandomInteger()
{
	return m_RandomDistribution(m_RandomGenerator);
}